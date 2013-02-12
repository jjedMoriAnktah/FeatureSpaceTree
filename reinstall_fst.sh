#/bin/bash
sudo pip uninstall FeatureSpaceTree
rm ./dist/FeatureSpaceTree-.01.tar.gz
rm ./dist/FeatureSpaceTree-.01-py2.7.egg
python setup.py sdist bdist_egg
sudo pip install ./dist/FeatureSpaceTree-.01.tar.gz 
