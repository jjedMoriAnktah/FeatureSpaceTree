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
# Setup script for FeatureSpaceTree
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

from setuptools import setup, find_packages
import sys, os

version = '.01'

setup(name='FeatureSpaceTree',
      version=version,
      description="An easy way to perform preprocessing tasks in text-clasification",
      long_description="""FeatureSpaceTree is a framework for scientists and students of computer science that simplify the textual-feature-extraction and representation of documents. These are two common previous stages in text-classification.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='feature-extraction text-classification tex-mining preprocessing-text',
      maintainer='Adrian Pastor Lopez-Monroy',
      maintainer_email='pastor@ccc.inaoep.mx',
      author='Adrian Pastor Lopez-Monroy',
      author_email='pastor@ccc.inaoep.mx',
      url='https://github.com/beiceman/FeatureSpaceTree',
      license='Apache License, Version 2.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests', 'others']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [console_scripts]
      simple_exp = feature_space_tree.experiments.experiment_simple:main_function
      advanced_exp = feature_space_tree.experiments.experiment_advanced:main_function
      """
      )
