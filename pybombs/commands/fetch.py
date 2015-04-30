#
# Copyright 2015 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#
""" PyBOMBS command: fetch """

from pybombs.commands import PyBombsCmd
from pybombs import fetch
from pybombs import recipe

class PyBombsFetch(PyBombsCmd):
    """ Fetch a package """
    cmds = {
            'fetch': 'Download a packages source code into the current prefixes source directory.'
    }

    @staticmethod
    def setup_subparser(parser, cmd=None):
        """
        Set up a subparser for a specific command
        """
        parser.add_argument(
                'packages',
                help="List of packages to fetch",
                action='append',
                default=[],
                nargs='*'
        )
        parser.add_argument(
                '-a', '--all',
                help="Fetch all packages. Warning: May take a while, and consume some considerable disk space",
                action='store_true',
        )
        parser.add_argument(
                '--deps',
                help="Also fetch dependencies of packages",
                action='store_true',
        )

    def __init__(self, cmd, args):
        PyBombsCmd.__init__(self, cmd, args, load_recipes=True, require_prefix=True)
        self._args.packages = args.packages[0] # wat?
        if len(self._args.packages) == 0 and not args.all:
            self.log.error("No packages specified.")
            exit(1)
        if self._args.all:
            self._args.deps = False

    def run(self):
        """ Go, go, go! """
        recipe_list = []
        if self._args.all:
            self.log.debug("Loading all recipes")
            self._args.packages = self._recipe_manager.list_all()
        try:
            self.log.debug("Getting recipes for: {}".format(self._args.packages))
            recipe_list = [recipe.Recipe(self._recipe_manager.get_recipe_filename(x)) for x in self._args.packages if len(x)]
        except KeyError as e:
            self.log.error("Unknown recipe: {}".format(e))
            exit(1)
        for r in recipe_list:
            if not len(r.srcs):
                continue
            self.log.debug("Downloading {}".format(r.srcs[0]))
            fetcher = fetch.make_fetcher(r)
            fetcher.fetch(r)
            fetcher.get_version(r)

