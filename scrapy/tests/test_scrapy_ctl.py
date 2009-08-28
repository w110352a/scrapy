import os
from os.path import exists, join
import subprocess
from shutil import rmtree
import sys
from tempfile import mkdtemp
from unittest import TestCase

import scrapy
from scrapy.conf import settings


class ProjectTest(TestCase):
    project_name = 'testproject'

    def setUp(self):
        self.temp_path = mkdtemp()
        self.cwd = self.temp_path

    def tearDown(self):
        rmtree(self.temp_path)

    def call(self, new_args, **kwargs):
        out = os.tmpfile()
        args = [sys.executable, '-m', 'scrapy.command.cmdline']
        args.extend(new_args)

        env = self.env if hasattr(self, 'env') else os.environ

        return subprocess.call(args, stdout=out, stderr=out, cwd=self.cwd, \
                               env=env, **kwargs)


class ScrapyCtlStartprojectTest(ProjectTest):
    
    def test_startproject(self):
        proj_path = join(self.temp_path, self.project_name)
        proj_mod_path = join(proj_path, self.project_name)

        ret = self.call(['startproject', self.project_name])
        self.assertEqual(ret, 0)

        self.assertEqual(exists(join(proj_path, 'scrapy-ctl.py')), True)
        self.assertEqual(exists(join(proj_path, 'testproject')), True)
        self.assertEqual(exists(join(proj_mod_path, '__init__.py')), True)
        self.assertEqual(exists(join(proj_mod_path, 'items.py')), True)
        self.assertEqual(exists(join(proj_mod_path, 'pipelines.py')), True)
        self.assertEqual(exists(join(proj_mod_path, 'settings.py')), True)
        self.assertEqual(exists(join(proj_mod_path, 'spiders', '__init__.py')), True)

        ret = self.call(['startproject', self.project_name])
        self.assertEqual(ret, 1)

        ret = self.call(['startproject', 'wrong---project---name'])
        self.assertEqual(ret, 1)


class CommandTest(ProjectTest):

    def setUp(self):
        super(CommandTest, self).setUp()

        self.call(['startproject', self.project_name])

        self.cwd = join(self.temp_path, self.project_name)

        self.env = os.environ.copy()
        self.env.pop('SCRAPY_SETTINGS_DISABLED', None)
        self.env['SCRAPY_SETTINGS_MODULE'] = '%s.settings' % self.project_name


class ScrapyCtlCommandsTest(CommandTest):

    def test_crawl(self):
        ret = self.call(['crawl'])
        self.assertEqual(ret, 0)

    def test_genspider_subcommands(self):
        ret = self.call(['genspider', '--list'])
        self.assertEqual(ret, 0)

        ret = self.call(['genspider', '--dump'])
        self.assertEqual(ret, 0)

        ret = self.call(['genspider', '--dump', '--template=basic'])
        self.assertEqual(ret, 0)

    def test_list(self):
        ret = self.call(['list'])
        self.assertEqual(ret, 0)


class BaseGenspiderTest(CommandTest):
    template = 'basic'

    def test_genspider(self):
        ret = self.call(['genspider', 'testspider', 'test.com',
                          '--template=%s' % self.template])
        self.assertEqual(ret, 0)
        self.assertEqual(os.path.exists(join(self.cwd, self.project_name, \
            'spiders', 'testspider.py')), True)

        ret = self.call(['genspider', 'otherspider', 'test.com'])
        self.assertEqual(ret, 1)

    
class CrawlGenspiderTest(BaseGenspiderTest):
    template = 'crawl'


class CsvFeedGenspiderTest(BaseGenspiderTest):
    template = 'csvfeed'


class XMLFeedGenspiderTest(BaseGenspiderTest):
    template = 'xmlfeed'
