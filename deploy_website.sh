set -ex

#REPO="git@github.com:feng-tao/amundsen.git"
#DIR=temp-clone

# Delete any existing temporary website clone.
#rm -rf $DIR

# Clone the current repo into temp folder.
#git clone $REPO $DIR

# Move working directory into temp folder.
#cd $DIR

# Build the site and push the new files up to GitHub.
mkdocs gh-deploy
git checkout gh-pages
git push

# Delete our temp folder.
#cd ..
#rm -rf $DIR
