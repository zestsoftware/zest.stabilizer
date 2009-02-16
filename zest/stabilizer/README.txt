Zest buildout stabilizer
========================

**Goal of this product**: zest.stabilizer helps moving the trunk checkouts in
your development buildout to tag checkouts in your production buildout. It
detects the latest tag and changes stable.cfg accordingly.

It is at the moment quite `Zest software <http://zestsoftware.nl>`_ specific
in the sense that it is hardcoded to two assumptions/requirements that are
true for us.


Requirement 1: split buildout configs
-------------------------------------

At Zest software, we've settled on a specific buildout.cfg setup that
separates the buildout.cfg into five files:

unstable.cfg
    Trunk checkouts, development eggs, development settings.

stable.cfg
    Tag checkouts, released eggs. No development products.

devel.cfg/preview.cfg/production.cfg
    Symlinked as production.cfg. The parts of the configuration that differ on
    development laptops, the preview and the production system. Port numbers,
    varnish installation, etc. Devel extends unstable, preview and production
    extend stable.    

zest.stabilizer thus moves the trunk checkouts in unstable.cfg to tag
checkouts in stable.cfg.


Requirement 2: infrae.subversion instead of svn:externals
---------------------------------------------------------

Our internal policy is to keep as much configuration in the buildout
config. So we've switched from svn:externals in ``src/`` to
infrae.subversion.  We extended infrae.subversion to support development eggs
and to support placement in a different directory from the default
``parts/[partname]/``.

Zest.stabilizer expects a specific name ("ourpackages"). Such a part looks
like this::

 [ourpackages]
 recipe = infrae.subversion >= 1.4
 urls =
     https://svn.vanrees.org/svn/reinout/anker/anker.theme/trunk anker.theme
     http://codespeak.net/svn/z3/deliverance/trunk Deliverance
 as_eggs = true
 location = src


What zest.stabilizer does
-------------------------

When you run ``stabilize``, zest.stabilizer does the following:

* Detect the ``[ourpackages]`` section in unstable.cfg and read in the urls.

* Remove "trunk" from each url and add "tags" and look up the available tags in
  svn.

* Grab the highest number for each.

* Remove existing ``[ourpackages]`` in stable.cfg if it exists.

* Add ``[ourpackages]`` part into stable.cfg with those highest available tag
  checkouts in it.

* Show the "svn diff" and ask you whether to commit the change.


Helper command: ``needrelease``
-------------------------------

Before stabilization, often a set of products first needs to be released. If
you have multiple packages, it is a chore to check all the svn logs to see if
there's a change since the last release.

Run ``needrelease`` and you'll get the last svn log message of every detected package.


Installation
------------

Installation is a simple ``easy_install zest.stabilizer``.

zest.stabilizer requires zest.releaser, which is installed automatically as a
dependency. Wow, more goodies!


Included programs
-----------------

Two programs are installed globally:

* ``unstable_fixup`` which currently only assists with moving ``src/*``
  development eggs to an infrae.subversion part. At the end it prints
  instructions for further work that you have to do manually.

* ``stabilize`` which takes the infrae.subversion part of ``unstable.cfg``
  and finds out the latest tags for each of those development packages. It
  then adds a similar part to ``stable.cfg``.
