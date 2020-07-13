from pprint import pprint
from selenium import webdriver
from settings_local import *
from elements import *


BASE_URL = 'site.example.com'
LOGIN_URL = BASE_URL + '/users/sign_in'
LOGOUT_URL = BASE_URL + '/users/sign_out'
GROUPS_URL = BASE_URL + '/teacher/groups'
GROUP_URL = GROUPS_URL + '/{id}'
RESULTS_URL = BASE_URL + '/results/{id}'


class Collector():
    def __init__(self):
        self.browser = webdriver.Chrome()

    def exit(self):
        self.browser.close()

    def log_in(self, username, password):
        self.browser.get(LOGIN_URL)
        self.browser.find_element_by_xpath(Login.login_input).send_keys(username)
        self.browser.find_element_by_xpath(Login.password_input).send_keys(password)
        self.browser.find_element_by_xpath(Login.submit_btn).click()

    def log_out(self):
        # Why does it use DELETE method?!
        self.browser.get(LOGOUT_URL)

    def get_group_id(self, group_name):
        self.browser.get(GROUPS_URL)
        group_id = self.browser.find_element_by_xpath(Groups.group_id.format(group_name=group_name))
        return int(group_id.text)

    def get_group_ids(self, *group_names):
        self.browser.get(GROUPS_URL)
        group_ids = []
        for group_name in group_names:
            group_id = self.browser.find_element_by_xpath(Groups.group_id.format(group_name=group_name))
            group_ids.append(int(group_id.text))
        return group_ids

    def get_group_students(self, group_id):
        self.browser.get(GROUP_URL.format(id=group_id))
        data = {}
        student_rows = self.browser.find_elements_by_xpath(Students.student_rows)
        for row in student_rows:
            name = row.find_element_by_xpath(Students.student_name)
            link = row.find_element_by_xpath(Students.student_link)
            student_name = name.text
            student_id = int(link.get_attribute('href').split('/')[-1])
            data[student_name] = student_id
        return data

    def get_groups_students(self, *group_ids):
        all_data = {}
        for group_id in group_ids:
            data = self.get_group_students(group_id)
            all_data[group_id] = data
        return all_data

    def get_hw_marks(self, period_start, avg_for=None):
        marks = self.browser.find_elements_by_xpath(Marks.hw_marks.format(period_start=period_start))
        mark_values = [float(mark.text) if mark.text else 0.0 for mark in marks]
        if not avg_for:
            avg_for = len(mark_values)
        return sum(mark_values) * 100 / (avg_for * 10)

    def get_student_marks(self, student_id, period_start, recount_hw=None):
        self.browser.get(RESULTS_URL.format(id=student_id))
        marks = self.browser.find_elements_by_xpath(Marks.marks.format(period_start=period_start))
        # домашки - посещаемость - контрольная - итого
        mark_values = [float(mark.text) if mark.text else 0.0 for mark in marks]
        if recount_hw:
            mark_values[0] = self.get_hw_marks(period_start, avg_for=recount_hw)
        if recount_hw or mark_values[-1] == 0:
            mark_values[-1] = round(mark_values[0] * 0.4 + mark_values[1] * 0.1 + mark_values[2] * 0.5, 0)
        return mark_values

    def get_sliced(self, student_id, period_start, slice, extra, extra_slice, recount=8):
        self.browser.get(RESULTS_URL.format(id=student_id))
        hw_marks = self.browser.find_elements_by_xpath(Marks.hw_marks.format(period_start=period_start))
        extra_hw_marks = self.browser.find_elements_by_xpath(Marks.hw_marks.format(period_start=extra))
        hw_marks_values = [float(mark.text) if mark.text else 0.0 for mark in hw_marks[slice[0]:slice[1]]] + \
            [float(mark.text) if mark.text else 0.0 for mark in extra_hw_marks[extra_slice[0]:extra_slice[1]]]
        # print(hw_marks_values)
        presence = self.browser.find_elements_by_xpath(Marks.presence.format(period_start=period_start))
        extra_presence = self.browser.find_elements_by_xpath(Marks.presence.format(period_start=extra))
        presence_values = [1 for value in (presence + extra_presence) if value.text.strip() == '+']
        marks_values = self.browser.find_elements_by_xpath(Marks.marks.format(period_start=period_start))
        avg_hw = sum(hw_marks_values) * 100 / (recount * 10)
        avg_presence = sum(presence_values) * 100 / recount
        exam = float(marks_values[2].text) if marks_values[2].text else 0.0
        total = round(avg_hw * 0.4 + avg_presence * 0.1 + exam * 0.5, 0)
        print(avg_hw, avg_presence, exam, total)
        return avg_hw, avg_presence, exam, total


def group_scan():
    collector = Collector()
    try:
        collector.log_in(LOGIN, PASSWORD)
        group_ids = collector.get_group_ids('Group 1', 'Group 2')
        print(group_ids)
        students_data = collector.get_groups_students(*group_ids)
        pprint(students_data)
    finally:
        collector.exit()

def main():
    collector = Collector()
    try:
        collector.log_in(LOGIN, PASSWORD)
        
        period_starts = []  # fill this manually for now

        for group_id, period_start in zip(GROUPS, period_starts):
            results = []
            print("\n{group_id}".format(group_id=group_id))
            for student_name, student_id in STUDENTS[group_id].items():
                try:
                    # that's broken crm
                    # if student_name in STUDENTS[14]:
                    #     marks = collector.get_sliced(student_id, period_start, (3, 8),
                    #                                  extra='2019.10.22', extra_slice=(0, 3))
                    # else:
                    #     marks = collector.get_student_marks(student_id, period_start)
                    marks = collector.get_student_marks(student_id, period_start)
                    results.append((student_name, marks[-1]))
                except:
                    print(f"Student {student_name} has no marks in period {period_start}")
            results.sort(key=lambda x: x[1], reverse=True)
            for result in results:
                print(*result)
    finally:
        collector.exit()



if __name__ == '__main__':
    main()
