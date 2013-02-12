FeatureSpaceTree
==========

Author: Adrian Pastor Lopez-Monroy, M.Sc., <pastor@ccc.inaoep.mx>
        Language Technologies Lab,
        Department of Computer Science,
        Instituto Nacional de Astrofísica, Óptica y Electrónica

Copyright (C) 2011-2012 FeatureSpaceTree Project
For license information, see LICENSE.txt

Welcome to FeatureSpaceTree,

I created FeatureSpaceTree because I wanted an easy way to perform
text-preprocessing in text-classification tasks.

FeatureSpaceTree is a framework for scientists and students of computer science
that facilitates the textual-feature-extraction and representation of documents.
These are two common previous stages in text-classification.

Currently there are very powerful tools to perform machine learning in a very
simple way (e.g. Weka on Java, Spider on Matlab). However, feature-extraction
and representation of documents is another matter. Normally, we program the
modules directly in a scripting programming language (e.g. perl, python),
especially when the task is small. Other times we use some libraries that
provide many of the common functions (e.g. NLTK, Apache UIMA). These last tools
are the big boys of Natural Language Processing. However, the learning curve
can be scared, and normally we ended assembling the union of several components
and witring a lot of lines of code.

FeatureSpaceTree aims to be a tool for feature-extraction and representation of
documents. The main idea is just stating what features you want to extract and
some representation. This is, on the command line (future GUI) we chose
the terms (plus multiple filters used before and after the extraction) and
which representation will be used (using of multiple parameters for each
representation). and the better is, ...
Without programming a single line of code!!! ... obviously you can also use the
API inside your own code :-)

INSTALLATION
============
You will need the pip software (also needed to install NLTK) in order to install
FeatureSpaceTree. 

Type into a terminal the following command:

$ sudo pip install git+https://github.com/beiceman/FeatureSpaceTree.git#egg=FeatureSpaceTree

If no errors, then congratulations you can use FeatureSpaceTree:

$ simple_exp yaml_file_with_parameters.yaml


INTRODUCTION
============

The main idea is that you will specify the following data:

1. - What attributes are needed to extract from the document corpus
(punctuation, words, n-grams at the character level, n-grams at word level,
word length, sentence length).

2. - Which filters will be applied to extract each of the attributes
(the n most frequent, n random, etc.). You could use filter on the text
before the term is extracted (e.g. eliminate capital letters). You could use
filter on tokens extracted (e.g. apply lematization).

3. - What representations will be used for these attributes, for example:
	* Bag of Words (BoW)
	* Latent Semantic Analysis (LSA)
	* Concise Semantic Analysis (CSA)
	* Bag of Terms (BoT)
	* Document Ocurrence Representation (DOR)
	* Term Cocurrence Representation (TCOR)

* Although the main idea is that SpaceTree works as a whole,
it is important to say that at the same time it is flexible to:

1. - Use each module independently.
2. - Extend the functionality with new modules of terms, filters
     and representations.

The output of SpaceTree will be:

1.- The representation of documents in a know format (currently just weka ".arff"
 and CSV format is available, however you can easily add other custom formats).
2.- A Yaml file which specify the edges of the spaces for each attribute
(ok better see the example :-) ).
3.- The vocabulary corpus for each space of attributes
4.- Some files with useful information to analyze.

VERSION
=======
.01

HOW IT WORKS?
=============

Initially SpaceTree works through the command line interface. It runs the main script and
parameters are provided through a YAML file (thanks to this, also would be easy to develop
a GUI that only treat YAML files).

$ simple_exp /somewhere/my_parameters.yaml 

An example of a YAML file is:

config_base:

  categories: [cat1, cat2, cat3]
  experiment_base_path: /home/aplm/Experimentos/validaciones/bow/exp_validacion
  experiment_name: exp_validacion
  processing_option: EnumTermsProcessing.SIMPLE

  corpus:
    type_corpus: EnumCommonTemplate.TRAIN_TEST

    train_corpus:
      corpus_path: /home/aplm/nltk_data/corpora/validacion/train
      filters_corpus:
      - type_filter_corpus: EnumFiltersCorpus.FULL
    
    test_corpus:
      corpus_path: /home/aplm/nltk_data/corpora/validacion/test
      filters_corpus:
      - type_filter_corpus: EnumFiltersCorpus.FULL

  # here there are parameters that can be loaded for your classification program.
  # For example, the following parameters are needed for a java program based on weka.
  # It means, perform 1 fold, with four classifiers into a voting scheme.
  
  java_args:
    n_folds: 10
    n_classifiers: 1
    classifiers_options:
    - classifier: SVM
    ensemble: SINGLE
    
# Once the corpus is specified, you will tell to SpaceTree what you want to extract.
# It is done through a tree scheme, where in the nodes you specify what attributes
# are going to be extracted and filtered. An in the leafs you will specify How
# those attributes will be represented.

# ==========================================================================
# root
# ==========================================================================
root:

  terms:

    # term
  - type_term: EnumTermLex.REG_EXP
    id_term: '1'
    regexp: "[a-zA-Z'ÁÉÍÓÚáéíóúñÑüÜ]+-*[a-zA-Z'ÁÉÍÓÚáéíóúñÑüÜ]+|[a-zA-Z'ÁÉÍÓÚáéíóúñÑüÜ]+|[.]+|[/,$?:;!()&%#=+{}*~.]+|[0-9]+"
    string: ''
    lazy: true
    mode: 0
    raw_string_normalizers: 
    - {type_raw_string_normalizer: EnumDecoratorRawStringNormalizer.TO_LOWER}
    filters_terms:
    - {type_filter_terms: EnumFiltersTermsList.FIXED_TOP, fixed_top: 20000}

  filters_terms:
    - {type_filter_terms: EnumFiltersTermsList.FIXED_TOP, fixed_top: 20000}


  childs:
  
    # ==========================================================================
    # subspace 1
    # ==========================================================================
  - representation: EnumRepresentation.BOW
    terms:
      # term
    - id_term: "1"
      filters_terms:
      - {type_filter_terms: EnumFiltersTermsList.FIXED_TOP, fixed_top: 20000}

    # space filters terms
    filters_terms:
    - {type_filter_terms: EnumFiltersTermsList.FIXED_TOP, fixed_top: 20000}


    childs: []
    # ========================================================================== 
    
    

################################################################################



Another example could be:

config_base:

  categories: [classname_1, classname_2, classname_n]
  experiment_base_path: /somewhere/my_firts_experiment
  experiment_name: my_firts_experiment
  processing_option: EnumTermsProcessing.SIMPLE

  test_corpus:
    corpus_path: /somewhere/my_corpus/test_documents
    filters_corpus:
    - type_filter_corpus: EnumFiltersCorpus.IMBALANCE # How many documents to test for each class?
      imbalance: [100, 100, 100]

  train_corpus:
    corpus_path: /somewhere/my_corpus/train_documents
    filters_corpus:
    - type_filter_corpus: EnumFiltersCorpus.IMBALANCE # How many documents to train for each class?
      imbalance: [100, 100, 100]

  # here there are parameters that can be loaded for your classification program.
  # For example, the following parameters are needed for a java program based on weka.
  # It means, perform 1 fold, with four classifiers into a voting scheme.
  java_args:
    n_folds: 1
    n_classifiers: 4
    classifiers_options:
    - classifier: SVM
    - classifier: SVM
    - classifier: SVM
    - classifier: SVM
    ensemble: SINGLE

# Once the corpus is specified, you will tell to SpaceTree what you want to extract.
# It is done through a tree scheme, where in the nodes you specify what attributes
# are going to be extracted and filtered. An in the leafs you will specify How
# those attributes will be represented.

# ==========================================================================
# root
# ==========================================================================
root:

  terms:
    # term
  - type_term: EnumTermLex.REG_EXP
    id_term: '1'
    regexp: "[a-zA-Z']+-*[a-zA-Z']+"
    boolStem: false
    string: ''
    lazy: true
    mode: 0
    filters_terms:
    - {type_filter_terms: EnumFiltersTermsList.FIXED_TOP, fixed_top: 200}

  - type_term: EnumTermLex.TOKEN_LEN
    id_term: '2'
    regexp: "[a-zA-Z']+-*[a-zA-Z']+"
    boolStem: false
    string: ''
    template: "Token{len:%s}"
    lazy: true
    mode: 0
    filters_terms:
    - {type_filter_terms: EnumFiltersTermsList.FIXED_TOP, fixed_top: 200}

    # term
  - type_term: EnumTermLex.BIGRAM
    id_term: '3'
    regexp: "[a-zA-Z']+-*[a-zA-Z']+"
    boolStem: true
    string: ''
    lazy: true
    mode: 0
    filters_terms:
    - {type_filter_terms: EnumFiltersTermsList.FIXED_TOP, fixed_top: 600}

  filters_terms:
    - {type_filter_terms: EnumFiltersTermsList.FIXED_TOP, fixed_top: 1000}


  childs:

    # ==========================================================================
    # subspace 1
    # ==========================================================================
  # As this is a leaf, then you will specify you representation (BOW = Bag of Terms).
  - representation: EnumRepresentation.BOW

    # As this is a leaf, then you will specify which attributes wants for this representation.
    terms:
      # term
    - id_term: "1"
      filters_terms: # This is "I want the 200 most frequent tokens"
      - {type_filter_terms: EnumFiltersTermsList.FIXED_TOP, fixed_top: 200}

      # term
    - id_term: "2"
      filters_terms: # This is "I want the 200 most frequent length of tokens"
      - {type_filter_terms: EnumFiltersTermsList.FIXED_TOP, fixed_top: 200}

      # term
    - id_term: "3"
      filters_terms: # This is "I want the 200 most frequent bigrams"
      - {type_filter_terms: EnumFiltersTermsList.FIXED_TOP, fixed_top: 600}

    # space filters terms
    filters_terms: # this is the total of terms in this subspace and in the BOW
    - {type_filter_terms: EnumFiltersTermsList.FIXED_TOP, fixed_top: 1000}


    childs: []
    # ==========================================================================

    # Here you could specify another subspace that uses some of the attributes in
    # the root, but using other filters and representations.
