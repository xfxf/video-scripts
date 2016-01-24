# git mirror workflow

The avserver has a directory `/var/www/html/lca/`.  This is served up using `git-http-backend` at http://avserver/git/

Raw files are accessible at http://avserver/lca/, but git needs a server side component in order to serve up packfiles.

This has some crib notes to help with managing the files.  [Pro Git](https://git-scm.com/book/en/v2) has longer form examples of working with git.

Be careful with submodules in this environment, as the client machines will not be able to access the upstream server.

## Adding a repository

**Note:** For third-party respositories, it is advisable to fork the upstream repository, and manage the commits that flow onto master.  Especially if upstream is volatile.

```
cd /var/www/html/lca/
git clone --mirror https://github.com/example/repository.git
```

Then on the client machine

```
git clone http://avserver/git/repository.git
```

## Updating the contents of a repository

On `avserver`:

```
cd /var/www/html/lca/example.git
git remote update
```

On client machines:

```
cd ~/lca/example
git pull
```

## Rolling back to a particular commit

You will need to know the commit ID you want to revert.  You can also revert multiple commits by specifying multiple at the command line.

This can have interesting results if the commit is not the latest, and some merging may be required in order to get the working tree in the state you want.

You can **also** make the edits manually and commit them as normal.  We will have a history, unless you force-push.

On your laptop:

```
cd ~/example
git revert 12345abcd
git push
```

Worked example:

```
$ cat foo
good
$ echo "bad" > foo
$ cat foo
good
bad
$ git add foo
$ git commit -m 'my bad commit'
[master 98598b8] my bad commit
 1 file changed, 1 insertion(+), 1 deletion(-)
$ git push

$ git revert 98598b8
... editor appears to write note
[master 848314f] Revert "foo 2"
 1 file changed, 1 insertion(+), 1 deletion(-)
$ cat foo
good
$ git push
```

Then follow the instructions for updating the repository above to push it out to the client machines.

