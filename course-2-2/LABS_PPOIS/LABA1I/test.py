import unittest
from unittest.mock import patch, MagicMock
from commission import Commission
from committeeman import Committeeman
from diploma_project import DiplomaProject, DiplomaProjectDict
from scientific_director import ScientificDirector
from student import Student


class TestCommission(unittest.TestCase):

    def setUp(self):
        self.commission = Commission()

    @patch('builtins.input', side_effect=[
        'Иванов',  # фамилия
        'Иван',    # имя
        'Иванович', # отчество
        'Инженер'  # профессия
    ])
    @patch('random.randrange', return_value=85)  # сложность
    @patch('builtins.print')  # чтобы не засорять вывод при тестах
    def test_add_committeeman(self, mock_print, mock_rand, mock_input):
        self.commission.add_committeeman()
        self.assertEqual(len(self.commission._Commission__commission), 1)

    @patch('builtins.input', side_effect=[
        'Иванов', 'Иван', 'Иванович', 'Инженер',
        'Петров', 'Петр', 'Петрович', 'Учёный',
        'Сидоров', 'Сидор', 'Сидорович', 'Эксперт'
    ])
    @patch('random.randrange', side_effect=[85, 90, 95])
    @patch('builtins.print')
    def test_full_commission(self, mock_print, mock_rand, mock_input):
        self.commission.add_committeeman()
        self.commission.add_committeeman()
        self.commission.add_committeeman()

        self.assertTrue(self.commission.commission_is())

    @patch('time.sleep', return_value=None)
    @patch('builtins.print')  # Чтобы не мусорить в консоль
    def test_rehearsal_diploma_project_pass(self, mock_print, mock_sleep):
        self.commission._Commission__max_difficulty = 90
        self.commission._Commission__upcoming_before_max_difficulty = 85

        result = self.commission.rehearsal_diploma_project({
            'presentation': 85,
            'report': 90
        })

        self.assertTrue(result)

    @patch('time.sleep', return_value=None)
    @patch('builtins.print')
    def test_rehearsal_diploma_project_fail_on_presentation(self, mock_print, mock_sleep):
        self.commission._Commission__max_difficulty = 90
        self.commission._Commission__upcoming_before_max_difficulty = 85

        result = self.commission.rehearsal_diploma_project({
            'presentation': 80,
            'report': 90
        })

        self.assertFalse(result)

    @patch('time.sleep', return_value=None)
    @patch('builtins.print')
    def test_rehearsal_diploma_project_fail_on_report(self, mock_print, mock_sleep):
        self.commission._Commission__max_difficulty = 90
        self.commission._Commission__upcoming_before_max_difficulty = 85

        result = self.commission.rehearsal_diploma_project({
            'presentation': 85,
            'report': 85
        })

        self.assertFalse(result)

    def test_get_max_difficulty_initial(self):
        self.assertEqual(self.commission.get_max_difficulty(), 0)


class TestDiplomaProject(unittest.TestCase):

    def setUp(self):
        self.project = DiplomaProject()

    @patch('random.randrange', return_value=50)
    @patch('builtins.print')
    def test_presentation_create(self, mock_print, mock_randrange):
        self.project.presentation_create()
        presentation = self.project.get_diploma_project()['presentation']
        self.assertTrue(20 <= presentation <= 100)

    @patch('random.randrange', return_value=60)
    @patch('builtins.print')
    def test_report_create(self, mock_print, mock_randrange):
        self.project.report_create()
        report = self.project.get_diploma_project()['report']
        self.assertTrue(20 <= report <= 100)

    @patch('random.randrange', return_value=20)
    @patch('builtins.print')
    def test_presentation_revision(self, mock_print, mock_randrange):
        self.project.presentation_create()  # создаем презентацию, будет 20 + 50 = 70
        self.project.presentation_revision()  # ревизия добавит еще 20, будет 90
        presentation = self.project.get_diploma_project()['presentation']
        self.assertTrue(20 <= presentation <= 100)

    @patch('random.randrange', return_value=30)
    @patch('builtins.print')
    def test_report_revision(self, mock_print, mock_randrange):
        self.project.report_create()  # создаем отчет
        self.project.report_revision()  # ревизия добавит еще 30
        report = self.project.get_diploma_project()['report']
        self.assertTrue(20 <= report <= 100)

    def test_get_diploma_project_initial(self):
        expected = {'presentation': 0, 'report': 0}
        self.assertEqual(self.project.get_diploma_project(), expected)

    def test_set_and_get_mark(self):
        self.project.set_mark(5)
        self.assertEqual(self.project.get_mark(), 5)


class TestScientificDirector(unittest.TestCase):

    def setUp(self):
        self.director = ScientificDirector()

    @patch('builtins.input', side_effect=['Иванов', 'Иван', 'Иванович'])
    @patch('builtins.print')
    def test_add_scientific_director(self, mock_print, mock_input):
        self.director.add_scientific_director()
        self.assertEqual(self.director.get_first_name(), 'Иван')
        self.assertEqual(self.director.get_surname(), 'Иванович')

    @patch('builtins.print')
    def test_verification_fail_presentation(self, mock_print):
        diploma = DiplomaProjectDict(presentation=70, report=85)
        result = self.director.verification_of_the_graduation_project(diploma)
        self.assertFalse(result)
        mock_print.assert_any_call('Надо доделать презентацию, полнота раскрытия темы 70%')

    @patch('builtins.print')
    def test_verification_fail_report(self, mock_print):
        diploma = DiplomaProjectDict(presentation=80, report=75)
        result = self.director.verification_of_the_graduation_project(diploma)
        self.assertFalse(result)
        mock_print.assert_any_call('Надо доделать доклад, полнота раскрытия темы 75% ')

    @patch('builtins.print')
    def test_verification_success(self, mock_print):
        diploma = DiplomaProjectDict(presentation=85, report=90)
        result = self.director.verification_of_the_graduation_project(diploma)
        self.assertTrue(result)
        mock_print.assert_called_with('Все хорошо, можно показывать')

    def test_is_exist(self):
        self.director._surname = 'Иванович'
        self.assertTrue(self.director.is_exist())

        self.director._surname = ''
        self.assertFalse(self.director.is_exist())


class TestStudent(unittest.TestCase):

    def setUp(self):
        self.student = Student()

    @patch('builtins.input', side_effect=['Петров', 'Петр', 'Петрович'])
    @patch('builtins.print')
    def test_add_student(self, mock_print, mock_input):
        self.student.add_student()
        self.assertEqual(self.student._first_name, 'Петр')
        self.assertEqual(self.student._surname, 'Петрович')

    @patch('builtins.print')
    @patch('time.sleep')
    @patch('random.randrange', return_value=50)
    def test_create_presentation(self, mock_rand, mock_sleep, mock_print):
        self.student.create_presentation()
        diploma = self.student.get_diploma_project()
        self.assertEqual(diploma['presentation'], 70)

    @patch('builtins.print')
    @patch('time.sleep')
    @patch('random.randrange', return_value=60)
    def test_create_report(self, mock_rand, mock_sleep, mock_print):
        self.student.create_report()
        diploma = self.student.get_diploma_project()
        self.assertEqual(diploma['report'], 80)

    @patch('builtins.print')
    @patch('random.randrange', return_value=10)
    def test_presentation_revision(self, mock_rand, mock_print):
        self.student.create_presentation()
        self.student.presentation_revision()
        diploma = self.student.get_diploma_project()
        self.assertTrue(20 <= diploma['presentation'] <= 100)

    @patch('builtins.print')
    @patch('random.randrange', return_value=15)
    def test_report_revision(self, mock_rand, mock_print):
        self.student.create_report()
        self.student.report_revision()
        diploma = self.student.get_diploma_project()
        self.assertTrue(20 <= diploma['report'] <= 100)

    def test_mark(self):
        self.student.set_mark(5)
        self.assertEqual(self.student.get_mark(), 5)


if __name__ == '__main__':
    unittest.main()

# coverage run -m unittest discover
# coverage report -m