# $ cd ~/repos/illumitag/
# $ git checkout --orphan gh-pages
# $ git rm -rf .
# $ echo "First commit" > index.html
# $ git add .
# $ git commit -m "Just to create the branch."
# $ git push origin gh-pages

git checkout gh-pages
rm -rf build _sources _static
git checkout master $(GH_PAGES_SOURCES)
git reset HEAD
make html
mv -fv build/html/* ./
rm -rf $(GH_PAGES_SOURCES) build
git add -A
git ci -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`" && git push origin gh-pages ; git checkout master
