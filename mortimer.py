#!/usr/bin/env python3
import shutil
import sys
import logging
import couchdb
import os
import argparse
import glob
import subprocess
import mrcfile
import pandas as pd
import skimage
import numpy as np
import time
from datetime import datetime

alignframes = shutil.which('alignframes')
edmont = shutil.which('edmont')
blendmont = shutil.which('blendmont')
extractpieces = shutil.which('extractpieces')

if any(x is None for x in [alignframes, edmont, blendmont, extractpieces]):
    logging.error('IMOD not in $PATH. Exiting.')
    sys.exit(1)

def process_tif(tif_path):
    logging.info(f'Processing {tif_path}')
    base, filename = os.path.split(tif_path)
    outfile = f'{base}/aligned_{filename.replace(".tif", ".mrc")}'

    image = skimage.io.imread(tif_path)
    if image.shape[2] == 3:
        aligned = skimage.color.rgb2gray(image)
        aligned = skimage.transform.resize(
            aligned,
            (aligned.shape[0] // 2, aligned.shape[1] // 2),
            anti_aliasing = True
        )
        aligned = skimage.img_as_ubyte(aligned)
        skimage.io.imsave(outfile.replace('mrc', 'png'), aligned)
        logging.info(f'Saved PNG: {outfile}')
    else:
        align_command = [
            alignframes,
            tif_path,
            outfile
        ]
        subprocess.run(align_command)
        logging.info('Finished aligning frames')

        with mrcfile.open(outfile) as f:
            aligned = f.data
        aligned = skimage.filters.gaussian(aligned, 3)
        aligned = skimage.transform.resize(
            aligned,
            (aligned.shape[0] // 10, aligned.shape[1] // 10),
            anti_aliasing = True
        )
        p2, p98 = np.percentile(aligned, (2, 98))
        aligned = skimage.exposure.rescale_intensity(aligned, in_range=(p2, p98))

        aligned = skimage.img_as_ubyte(aligned)
        skimage.io.imsave(outfile.replace('mrc', 'png'), aligned)
        logging.info(f'Saved PNG: {outfile}')

class Database(object):
    def __init__(self) -> None:
        host = os.environ['COUCHDB_HOST']
        username = os.environ['COUCHDB_USERNAME']
        password = os.environ['COUCHDB_PASSWORD']
        self.server = couchdb.Server(f'http://{username}:{password}@{host}:5984')

        if 'mortimer_sessions' in self.server:
            self.sessions_db = self.server['mortimer_sessions']
        else:
            self.sessions_db = self.server.create('mortimer_sessions')

    @property
    def sessions(self):
        session_dict = self.sessions_db.get('sessions')
        if session_dict is None:
            return []
        else:
            return [x for x in session_dict.keys() if x not in ['_id', '_rev']]

    def new_session(self, name:str, path:str) -> None:
        sessions = self.sessions_db.get('sessions')
        if sessions is None:
            sessions = {}
        
        sessions[name] = {
            'path': path
        }

        try:
            info = pd.read_csv(f'{path}/grid_info.csv')
            info = info[info['Screening Grid Number'].notna()]
            info = info.set_index('Screening Grid Number')
            info.fillna('', inplace=True)
            logging.debug(info)
            info = info.to_dict(orient = 'index')
            sessions[name]['grid_info'] = info
            logging.info('Found grid info:')
            logging.info(info)
        except FileNotFoundError:
            logging.warning('No grid info found in session root.')

        self.sessions_db['sessions'] = sessions

    def delete_session(self, session):
        session_dict = self.sessions_db.get('sessions')
        session_dict.pop(session)
        self.sessions_db['sessions'] = session_dict
        

def file_modtime(file):
    file_mtime = os.path.getmtime(file)
    return (datetime.now() - datetime.fromtimestamp(file_mtime)).total_seconds()

class Processor(object):
    def __init__(self, path:str, db:Database, grid_base, movie_base, mont_name) -> None:
        self.path = os.path.normpath(path)
        if path[-1] == '/':
            path = path[:-1]
        self.name = os.path.split(path)[1]
        self.grid_base = grid_base
        self.movie_base = movie_base
        self.mont_name = mont_name

        self._grids = glob.glob(f'{self.path}/{self.grid_base}*')
        self.db = db

        if self.name not in self.db.sessions:
            self.db.new_session(self.name, self.path)

    @property
    def grids(self):
        self._grids = glob.glob(f'{self.path}/{self.grid_base}*')
        return self._grids

    def find_new_montages(self):
        all_monts = []
        for grid in self.grids:
            if os.path.exists(f'{grid}/{self.mont_name}') and not os.path.exists(f'{grid}/aligned-{self.mont_name}') and file_modtime(f'{grid}/{self.mont_name}') > 60:
                all_monts.append(f'{grid}/{self.mont_name}')

        return all_monts
    
    # montaging code stolen from Hotspur
    def bin_montage_stack(self, mont):
        base, filename = os.path.split(mont)
        command = ' '.join([
            edmont,
            f'-imin {mont}',
            f'-imout {base + "/binned-" + filename}',
            '-mdoc',
            '-bin 4'
        ])
        logging.info(f'Binning montage for {os.path.split(base)[1]}')
        try:
            output = subprocess.run(command, shell=True, capture_output = True, check = True)
        except subprocess.CalledProcessError as e:
            logging.error('Subprocess exited with error during montage alignment:')
            logging.error(e.stderr)
            sys.exit(1)

    def extract_coords(self, mont):
        base, filename = os.path.split(mont)
        command = ' '.join([
            extractpieces,
            f'-input {base + "/binned-" + filename}',
            f'-output {mont[:-4] + ".coords"}'
        ])
        logging.info(f'Extracting coordinates for {os.path.split(base)[1]}')
        try:
            output = subprocess.run(command, shell = True, capture_output = True, check = True)
        except subprocess.CalledProcessError as e:
            logging.error('Subprocess exited with error during montage alignment:')
            logging.error(e.stderr)
            sys.exit(1)

    def blend_montage(self, mont):
        base, filename = os.path.split(mont)
        command = ' '.join([
            blendmont,
            f'-imin {base + "/binned-" + filename}',
            f'-imout {base + "/aligned-" + filename}',
            f'-plin {mont[:-4] + ".coords"}',
            f'-roo {base + "/aligned-" + filename}',
            '-sl -nofft'
        ])
        logging.info(f'Blending montage for {os.path.split(base)[1]}')
        logging.debug(f'Command: {command}')
        try:
            output = subprocess.run(command, shell = True, check = True)
        except subprocess.CalledProcessError as e:
            logging.error('Subprocess exited with error during montage alignment:')
            logging.error(e.stderr)
            sys.exit(1)

    def preview_montage(self, mont):
        base, filename = os.path.split(mont)
        with mrcfile.open(f'{base}/aligned-{filename}') as f:
            mont_image = f.data

        mont_image = skimage.exposure.equalize_adapthist(mont_image, clip_limit = 0.03)
        mont_image = skimage.img_as_ubyte(mont_image)
        skimage.io.imsave(
            f'{base}/lmm.png',
            mont_image
        )
        logging.info('Saved PNG')
        


    def find_new_files(self):
        all_tifs = []
        for grid in self.grids:
            all_tifs.extend(glob.glob(f'{grid}/{self.movie_base}*.tif'))

        tifs_to_process = []
        for tif in all_tifs:
            base, filename = os.path.split(tif)
            potential_processed = f'{base}/aligned_{filename}'.replace('.tif', '.png')
            logging.info(f'Checking if {potential_processed} exists...')
            if not os.path.exists(potential_processed) and file_modtime(tif) > 60:
                tifs_to_process.append(tif)
        
        return tifs_to_process

    def process_files(self):

        while True:

            new_montages = self.find_new_montages()
            while new_montages:
                mont_to_process = new_montages.pop()
                self.bin_montage_stack(mont_to_process)
                self.extract_coords(mont_to_process)
                self.blend_montage(mont_to_process)
                self.preview_montage(mont_to_process)

            need_processing = self.find_new_files()

            while need_processing:
                tif_to_process = need_processing.pop()
                process_tif(tif_to_process)
            
            need_processing = self.find_new_files()
            if not need_processing and not new_montages:
                logging.info('No new files detected. Waiting 10 seconds.')
                time.sleep(10)

def utilities(args):
    db = Database()

    if args.list_sessions:
        print('Sessions:', *db.sessions, sep = '\n  ')

    if args.session_info:
        print(db.sessions_db['sessions'][args.session_info]['grid_info'])

    if args.delete_session:
        db.delete_session(args.delete_session)

    if args.add_note:
        sessions = db.sessions_db['sessions']
        session = args.add_note[0]
        grid = args.add_note[1]
        note = args.add_note[2]

        prior_note = sessions[session]['grid_info'][grid]['Notes']
        if not prior_note:
            sessions[session]['grid_info'][grid]['Notes'] = note
        else:
            sessions[session]['grid_info'][grid]['Notes'] = prior_note + '\n' + note

        db.sessions_db['sessions'] = sessions

def process_session(args):
    db = Database()

    session = Processor(args.path, db, args.grid_base, args.movie_base, args.mont_name)
    session.process_files()

parser = argparse.ArgumentParser(
    description = 'Monitor a screening session'
)

verbosity = parser.add_argument_group('verbosity')
vxg = verbosity.add_mutually_exclusive_group()
vxg.add_argument(
    '-q', '--quiet',
    help = 'Print Errors only',
    action = 'store_const',
    dest = 'verbosity',
    const = 'q'
)
vxg.add_argument(
    '-v', '--verbose',
    help = 'Print Info, Warnings, and Errors. Default state.',
    action = 'store_const',
    dest = 'verbosity',
    const = 'v'
)
vxg.add_argument(
    '--debug',
    help = 'Print debug output.',
    action = 'store_const',
    dest = 'verbosity',
    const = 'd'
)

subparsers = parser.add_subparsers()

process = subparsers.add_parser('process', help = 'Process a session')
process.set_defaults(func = process_session)
process.add_argument(
    'path',
    help = 'Path of session to process'
)
process.add_argument(
    '--movie-base',
    help = 'Base name of movies. Default `frames_`',
    default = 'frames_'
)
process.add_argument(
    '--grid-base',
    help = 'Base name for grid directories. Default `grid`. Can be empty.',
    default = 'grid'
)
process.add_argument(
    '--mont-name',
    help = 'Name of LMM, without .mrc extension. Default `lmm`',
    default = 'lmm'
)

utils = subparsers.add_parser(
    'utilities',
    help = 'Mortimer utilities'
)
utils.set_defaults(func = utilities)
utils.add_argument(
    '--list-sessions',
    help = 'Which sessions currently available',
    action = 'store_true'
)
utils.add_argument(
    '--delete-session',
    help = 'Remove session from mortimer by name'
)
utils.add_argument(
    '--session-info',
    help = 'Get grid info for a session by name'
)
utils.add_argument(
    '--add-note',
    help = 'Add a note. {session} {grid} {note}',
    nargs = 3
)

if __name__ == "__main__":
    args = parser.parse_args()

    levels = {
        'q': logging.ERROR, 
        'v': logging.INFO,
        'd': logging.DEBUG
    }
    try:
        level = levels[args.verbosity]
    except KeyError:
        level = logging.INFO

    logging.basicConfig(
        level = level,
        format = '{levelname}: {message} ({filename})',
        style = '{'
    )

    args.func(args)