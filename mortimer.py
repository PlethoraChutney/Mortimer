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
import numpy as np
import skimage
import time

test_dir = '/goliath/rawdata/BaconguisLab/posert/Screening-20220617/'

alignframes = shutil.which('alignframes')

if alignframes is None:
    logging.error('dm2mrc or alignframes not found in $PATH. Exiting.')
    sys.exit(1)

def process_tif(tif_path):
    logging.info(f'Processing {tif_path}')
    outfile = tif_path.replace('frames', 'aligned').replace('tif', 'mrc')
    align_command = [
        alignframes,
        tif_path,
        outfile
    ]
    subprocess.run(align_command)
    logging.info('Finished aligning frames')

    with mrcfile.open(outfile) as f:
        aligned = f.data
    aligned = skimage.transform.resize(
        aligned,
        (aligned.shape[0] // 10, aligned.shape[1] // 10),
        anti_aliasing = True
    )
    aligned = skimage.exposure.equalize_adapthist(aligned, clip_limit = 0.03)
    aligned = skimage.img_as_ubyte(aligned)
    skimage.io.imsave(outfile.replace('mrc', 'png'), aligned)
    logging.info('Saved PNG')

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
            return list(session_dict.keys())

    def new_session(self, name:str, path:str) -> None:
        sessions = self.sessions_db.get('sessions')
        if sessions is None:
            sessions = {}
        
        sessions[name] = {
            'path': path
        }

class Processor(object):
    def __init__(self, path:str, db:Database) -> None:
        self.path = os.path.normpath(path)
        self.name = os.path.split(path)[1]
        self._grids = glob.glob(f'{self.path}/grid*')
        self.db = db

        if self.name not in self.db.sessions:
            self.db.new_session(self.name, self.path)

    @property
    def grids(self):
        self._grids = glob.glob(f'{self.path}/grid*')
        return self._grids

    def find_new_files(self):
        all_tifs = []
        for grid in self.grids:
            all_tifs.extend(glob.glob(f'{grid}/frames_*.tif'))

        tifs_to_process = []
        for tif in all_tifs:
            potential_processed = tif.replace('frames', 'aligned').replace('.tif', '.mrc')
            if not os.path.exists(potential_processed):
                tifs_to_process.append(tif)
        
        return tifs_to_process

    def process_files(self):
        need_processing = self.find_new_files()

        while True:
            while need_processing:
                tif_to_process = need_processing.pop()
                process_tif(tif_to_process)
            
            need_processing = self.find_new_files()
            if not need_processing:
                logging.info('No new files detected. Waiting 10 seconds.')
                time.sleep(10)

def utilities(args):
    db = Database()

    if args.list_sessions:
        print('Sessions:', *db.sessions, sep = '\n  ')

def process_session(args):
    db = Database()

    session = Processor(args.path, db)
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