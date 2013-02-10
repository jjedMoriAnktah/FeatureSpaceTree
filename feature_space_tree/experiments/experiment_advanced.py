#!/usr/local/bin/python
# coding: utf-8

# Copyright (C) 2011-2012 FeatureSpaceTree Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ==============================================================================
# FeatureSpaceTree: Experiment module
#
# Author: Adrian Pastor Lopez-Monroy <pastor@ccc.inaoep.mx>
# URL: <https://github.com/beiceman/FeatureSpaceTree>
#
# Language Technologies Lab,
# Department of Computer Science,
# Instituto Nacional de Astrofísica, Óptica y Electrónica
#
# For license information, see:
#  * The header of this file
#  * The LICENSE.TXT included in the project dir
# ==============================================================================

'''
Created on 26/11/2011

@author: Adrian Pastor Lopez-Monroy <pastor@ccc.inaoep.mx>

This script load the arguments from a YAML file, and builds a tree of feature
spaces, where each node includes term filtering, selection and representation.

usage:

python experiment_simple.py /somewhere/my_args.yaml
'''

import time
import yaml
import sys
import shutil
import re

#print sys.path

from ..representations import representations
from ..representations.representations import bcolors


def recursive_build(id_space,
          space_path,
          categories,
          train_corpus,
          test_corpus,
          corpus_file_list_train,
          corpus_file_list_test,
          kwargs_sub_space,
          processing_option,
          root):

    if len(kwargs_sub_space['childs']) >= 1:

        space_component = \
        representations.SpaceComposite(id_space,
                                       space_path,
                                       categories,
                                       train_corpus,
                                       test_corpus,
                                       corpus_file_list_train,
                                       corpus_file_list_test,
                                       kwargs_sub_space,
                                       processing_option,
                                       root)

        #tokens = space_component.tokens
        i = 1
        for kwargs_child in kwargs_sub_space['childs']:

            space_component.add(recursive_build(id_space + "." + str(i),
                                      (
                                        ("%s/%s")
                                        %
                                        (space_path,
                                         "sub_space" + id_space + "." + str(i))
                                      ),
                                      categories,
                                      train_corpus,
                                      test_corpus,
                                      corpus_file_list_train,
                                      corpus_file_list_test,
                                      kwargs_child,
                                      processing_option,
                                      space_component))
            i += 1

    else:
        space_component = representations.SpaceItem(id_space,
                                                    space_path,
                                    categories,
                                    train_corpus,
                                    test_corpus,
                                    corpus_file_list_train,
                                    corpus_file_list_test,
                                    kwargs_sub_space,
                                    processing_option,
                                    root)

    return space_component

def main_function():

    # FIXME: Here we are missing a validation for the arguments ...

    experiment_config_path = sys.argv[1]

    print 'Starting the principal script...'
    t1 = time.time()
    stream = file(experiment_config_path, 'r')

    # use the yaml module in order to put the parameters of the yaml file into
    # a python dictionary.
    global_kwargs_list = yaml.load(stream)
    # DEBUG: print global_kwargs_list

    # extrac just the necessary (at least for this framework) from the
    # yaml args dictionary.
    config_base = representations.ConfigBaseAdvanced(global_kwargs_list['config_base'],
                                                     global_kwargs_list)
    # ==========================================================================

    #===========================================================================
    # This begins the "population" of data. It treats the base case (the root).
    #===========================================================================

    # check how for each node, we have to load/construct "global" parameters
    # (e.g.the corpus, source).
    kwargs_root = global_kwargs_list['root']
    for kwargs_term in kwargs_root['terms']:
        kwargs_term['corpus'] = config_base.train_corpus
        kwargs_term['source'] = config_base.corpus_file_list_train
        kwargs_term['term_path'] = "%s" % (config_base.experiment_base_path)#,
    #                                           #config_base.experiment_name)

    root = representations.SpaceComposite("Root",
                                          (("%s/%s") %
                                           (config_base.experiment_base_path,
                                            config_base.experiment_name)),
                                          config_base.categories,
                                          config_base.train_corpus,
                                          config_base.test_corpus,
                                          config_base.corpus_file_list_train,
                                          config_base.corpus_file_list_test,
                                          kwargs_root,
                                          config_base.processing_option,
                                          None)


#    virtual_processor =\
#    virtuals.VocabularyVirtualProcessor(kwargs_root['terms'])
#    root.set_virtual_elements(virtual_processor.virtual_elements)

    #===========================================================================
    t2 = time.time()
    print representations.Util.get_string_fancy_time(t2 - t1,
                                                     'End of the root')
    #===========================================================================
    # This begins the recursive build of the subspaces
    #===========================================================================
    i = 1
    for kwargs_sub_space in kwargs_root['childs']:

        root.add(recursive_build(str(i),
                 (("%s/%s/%s") % (config_base.experiment_base_path,
                                  config_base.experiment_name,
                                  "sub_space_"+str(i))),
                 config_base.categories,
                 config_base.train_corpus,
                 config_base.test_corpus,
                 config_base.corpus_file_list_train,
                 config_base.corpus_file_list_test,
                 kwargs_sub_space,
                 config_base.processing_option,
                 root))

        i += 1#            virtual_processor = \
#            self.factory_processing.\
#            build_virtual_processor(self.kwargs_space['terms'])
#            self.set_virtual_elements(virtual_processor.virtual_elements)
    #===========================================================================
    t2 = time.time()
    print representations.Util.get_string_fancy_time(t2 - t1,
                                                     'End of the subspaces')

    #===========================================================================
    # Begins the iteration through the tree-space to build the representations.
    #===========================================================================
    root.create_space_properties()
    iterator = root.create_iterator()
    for e in iterator:
        print "================================================"
        print bcolors.HEADER + "Creating properties for id_space: " + str(e.id_space) + bcolors.ENDC
        print "path: " + str(e.space_path)
        e.create_space_properties()
        ##print "vocabulary: " + str(e.get_vocabulary)
        #print "f_dist: " + str(e.get_fdist())
        print "------------------------------------------------\n"
        print "Creating virtuals ..."
        try:
            e.create_virtuals()
        except representations.UnsupportedOperationError as error:
            print (error)
        print "------------------------------------------------\n"
        print "Creating representations ..."
        try:
            e.create_representation()
        except representations.UnsupportedOperationError as error:
            print (error)
        else:
            print "attributes: " + str(e.get_attributes())
            #print "matrix_train: " + str(e.get_matrix_train())
            #print "matrix_test: " + str(e.get_matrix_test())
        print "================================================\n\n"
    #===========================================================================

    corpora = representations.Corpora(config_base.experiment_base_path)
    corpora.generate()

    #===========================================================================
    # Writes a general report
    #===========================================================================
    report = representations.Report()
    report.generate_report(root,
                           config_base.experiment_name,
                           config_base.experiment_base_path,
                           config_base.global_kwargs_list)
    #===========================================================================

    print "arguments in: " + experiment_config_path
    print "backed up in: " + global_kwargs_list['config_base']['experiment_base_path'] + '/' + re.match('(.*/)?(.+\.yaml)', experiment_config_path).group(2)
    shutil.copyfile(experiment_config_path,
                    global_kwargs_list['config_base']['experiment_base_path'] + '/' + re.match('(.*/)?(.+\.yaml)', experiment_config_path).group(2))

    t2 = time.time()
    print representations.Util.get_string_fancy_time(t2 - t1,
                                                     'End of the principal script')

    

#if __name__ == '__main__':

    #main_function()