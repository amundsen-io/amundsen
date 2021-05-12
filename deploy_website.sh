set -ex

#REPO="git@github.com:amundsen-io/amundsen.git"
#DIR=temp-clone
# We use https://www.mkdocs.org/user-guide/deploying-your-docs/ to build/deploy docs
# Currently the doc is built/deployed manually. We should first build and deploy locally and verify it.
# Here are some basic steps:
# 1. virtualenv venv
# 2. source venv/bin/activate
# 3. pip3 install -r requirements.txt
# 4. brew install mkdocs
# 5. mkdocs serve # build locally and serve it in localhost:8000 . On mac OS, you may face ImportError and you may need to downgrade openssl by $ brew switch openssl 1.0.2r
# 6. mkdocs gh-deploy # deploy to gh page

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
