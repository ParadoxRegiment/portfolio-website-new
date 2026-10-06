from django.test import TestCase
from django.urls import reverse

from .models import Category, Project, Tag, ScriptDemo


class ProjectListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = Category.objects.create(name="Data Tools", slug="data-tools")
        web = Category.objects.create(name="Web Apps", slug="web-apps")
        sim = Category.objects.create(name="Simulations", slug="simulations")

        python = Tag.objects.create(name="Python", slug="python")
        sql = Tag.objects.create(name="SQL", slug="sql")
        django = Tag.objects.create(name="Django", slug="django")

        cls.make_project("ETL", data, [python, sql])
        cls.make_project("Site", web, [python, django])
        cls.make_project("Lightning", sim, [python])
        cls.make_project("Draft", data, [python], published=False)

        cls.url = reverse("projects:list")

    @classmethod
    def make_project(cls, title, category, tags, published=True):
        project = Project.objects.create(
            title=title,
            slug=title.lower(),
            summary="summary",
            description="description",
            category=category,
            is_published=published,
        )
        project.tags.set(tags)
        return project

    def titles(self, response):
        return {p.title for p in response.context["projects"]}

    # --- visibility ---
    def test_drafts_hidden_from_list(self):
        response = self.client.get(self.url)
        self.assertNotIn("Draft", self.titles(response))

    def test_draft_detail_returns_404(self):
        response = self.client.get(reverse("projects:detail", kwargs={"slug": "draft"}))
        self.assertEqual(response.status_code, 404)

    # --- filtering ---
    def test_tags_use_and_logic(self):
        response = self.client.get(self.url, {"tag": ["python", "sql"]})
        self.assertEqual(self.titles(response), {"ETL"})

    def test_categories_use_or_logic(self):
        response = self.client.get(self.url, {"category": ["data-tools", "web-apps"]})
        self.assertEqual(self.titles(response), {"ETL", "Site"})

    def test_category_and_tag_combined(self):
        response = self.client.get(
            self.url, {"category": ["web-apps", "simulations"], "tag": ["django"]}
        )
        self.assertEqual(self.titles(response), {"Site"})

    # --- htmx ---
    def test_htmx_request_returns_fragment(self):
        full = self.client.get(self.url)
        fragment = self.client.get(self.url, headers={"HX-Request": "true"})
        self.assertContains(full, "<html")
        self.assertNotContains(fragment, "<html")
        self.assertContains(fragment, 'id="results"')

    def test_vary_header_set(self):
        response = self.client.get(self.url)
        self.assertIn("HX-Request", response["Vary"])
        
class ScriptDemoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Simulations", slug="simulations")
        script = Project.objects.create(
            title="Walk", slug="walk", summary="s", description="d",
            category=category, is_published=True,
        )
        Project.objects.create(
            title="Site", slug="site", summary="s", description="d",
            category=category, is_published=True,
        )
        cls.demo = ScriptDemo.objects.create(
            project=script,
            source_zip="demos/walk.zip",   # a name is enough; the file isn't opened
            entry_point="walk.py",
            command="walk",
            packages="numpy, matplotlib,",
            examples="walk --help\n\nwalk -n 10\n",
        )

    def test_lists_parse_cleanly(self):
        self.assertEqual(self.demo.package_list, ["numpy", "matplotlib"])
        self.assertEqual(self.demo.example_list, ["walk --help", "walk -n 10"])

    def test_console_only_on_projects_with_a_demo(self):
        with_demo = self.client.get(reverse("projects:detail", kwargs={"slug": "walk"}))
        without_demo = self.client.get(reverse("projects:detail", kwargs={"slug": "site"}))
        self.assertContains(with_demo, "data-console")
        self.assertContains(with_demo, '"entryPoint": "walk.py"')
        self.assertNotContains(without_demo, "data-console")