class Login:
    login_input = '//input[@id="user_login"]'
    password_input = '//input[@id="user_password"]'
    submit_btn = '//input[@type="submit"]|button[@type="submit"]'


class Groups:
    group_id = '//td[text()="{group_name}"]/../th[1]'


class Students:
    student_rows = '(//table)[2]//tr[position()>1]'
    student_name = 'td[1]'
    student_link = 'td/a'


class Marks:
    period_start = '//div[@class="results-table-wrap"][text()[contains(.,"{period_start}")]][1]'
    marks = period_start + '//td[position()>last()-4]'
    hw_marks = period_start + '//td[position()<=last()-4]'
    presence = period_start + '//tbody//th[@scope="col"]'
