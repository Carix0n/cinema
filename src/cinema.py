import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3

class StylesHandler(tornado.web.RequestHandler):
    def get(self):
        template = tornado.template.Template('''
            .table_header{
                text-decoration: underline;
                font-style: italic;
                font-size:25px;
                color: Highlight;

            }
            table{
                text-align: center;
                font-size: 20px;
                font-style: normal;
                vertical-align: middle;
                border-spacing: 6px;
                border-collapse:separate;
                padding : 2px;
            }
            tr{
                border: 4px solid Black;
            }
            .hall{
                height: 25px;
                width: 25px;
                font-style: italic;
                color: Highlight;
            }
            a {text-decoration: none; font-size:25px;}
            a:hover { text-decoration: underline;}
        ''')
        self.write(template.generate())

class CinemaHandler(tornado.web.RequestHandler):
    def get(self):
        template = tornado.template.Template('''
            <html>
                <head>
                <title> Добро пожаловать на сайт кинотеатра</title>
                <link rel="stylesheet" href="../style.css">
                </head>
                <body>
                    <center>
                    <form action='/login' method='post'>
                            <label> Пользователь </label>
                        <br><input type='text' name='login'>
                        <br><label> Пароль </label>
                        <br><input type='password' name='password'>
                        <br>
                        <br><input type='submit' name='action' value="Вход">
                        <br>
                        <br><input type='submit' name='action' value="Регистрация">
                    </form>
                    </center>
                </body>
            </html>
        ''')
        self.write(template.generate())

class AuthoriseHandler(tornado.web.RequestHandler):
    def post(self):
        login = self.get_argument("login")
        password = self.get_argument("password")
        action = self.get_argument("action")
        connection = sqlite3.connect('../data/cinema.db')
        db_cursor = connection.cursor()
        query = 'select login, password from users'
        db_cursor.execute(query)
        user_base = db_cursor.fetchall()
        if action == "Вход":
            if login == 'admin' and password == 'admin':
                self.set_cookie("admin", '1')
                self.redirect('../menu')
            elif (login, password) in user_base:
                self.set_cookie("user", login)
                self.redirect('../menu')
            else:
                self.redirect('../login_error')
        else:
            dict_user_base = dict(user_base)
            if login == 'admin' or login in dict_user_base.keys():
                self.redirect('../registration_error')
            query = ("insert into users (login, password) values('"+login+"', '"+password+"')")
            db_cursor.execute(query)
            self.set_cookie("user", login)
            db_cursor = connection.cursor()
            query = ("insert into tickets (login, purchase_num) values('"+login+"', 0)")
            db_cursor.execute(query)
            connection.commit()
            self.redirect('../menu')

        connection.close()

class AuthoriseErrorHandler(tornado.web.RequestHandler):
    def get(self):
        template = tornado.template.Template('''
            <html>
                <head>
                    <title> Ошибка </title>
                    <link rel="stylesheet" href="../style.css">
                </head>
                <body>
                    <center>
                        Неверный логин или пароль
                        <form action="../" method="get">
                            <br> <input type="submit" value="Вернуться на главную">
                        </form>
                    </center>
                </body>
            </html>
        ''')
        self.write(template.generate())

class RegistrationErrorHandler(tornado.web.RequestHandler):
    def get(self):
        template = tornado.template.Template('''
            <html>
                <head>
                    <title> Ошибка </title>
                    <link rel="stylesheet" href="../style.css">
                </head>
                <body>
                    <center>
                        Пользователь с таким именем уже существует
                        <form action="../" method="get">
                            <br> <input type="submit" value="Вернуться на главную">
                        </form>
                    </center>
                </body>
            </html>
        ''')
        self.write(template.generate())

class MenuHandler(tornado.web.RequestHandler):
    def get(self):
        template = tornado.template.Template('''
            <html>
                <head>
                    <title> Главное меню </title>
                    <link rel="stylesheet" href="../style.css">
                </head>
                <body>
                    <center>
                        <br><a href="../films"> Фильмы </a><br>
                        <br><a href="../sessions"> Сеансы </a><br>
                        <br><a href="../halls"> Залы </a><br>
                    </center>
                </body>
            </html>
        ''')
        self.write(template.generate())

class FilmsHandler(tornado.web.RequestHandler):
    def get(self):
        connection = sqlite3.connect('../data/cinema.db')
        db_cursor = connection.cursor()
        query = 'select * from films'
        db_cursor.execute(query)
        query_res = db_cursor.fetchall()
        template = tornado.template.Template('''
            <html>
                <head>
                    <title> Films </title>
                    <link rel="stylesheet" href="../style.css">
                </head>
                <body>
                    <center>
                        Films
                        <br>
                        <a href="../menu"> Назад </a>
                        <br>
                        <table>
                            <tr>
                                <td class="table_header"> Название </td>
                                <td class="table_header"> Описание </td>
                                <td class="table_header"> Посмотреть сеансы </td>
                            </tr>
                            {% for i in data %}
                                <tr>
                                    <td> {{i[0]}} </td>
                                    <td> {{i[1]}} </td>
                                    <td>
                                        <center>
                                            <form  method='get' action='../sessions'>
                                                <input type='submit' name='film' value='{{i[0]}}'>
                                            </form>
                                        </center>
                                     </td>
                                </tr>
                            {%end%}
                        </table>
                    </center>
                </body>
            </html>
        ''')
        self.write(template.generate(data = query_res))

        connection.close()

class ChooseHandler(tornado.web.RequestHandler):
    def get(self):
        connection = sqlite3.connect('../data/cinema.db')
        db_cursor = connection.cursor()
        halls = db_cursor.execute('select hall_id from halls').fetchall()

        halls_list = ""
        for hall_id in halls:
            cur_id = hall_id[0]
            halls_list += "<a href = '../hall?id=%d'>Зал #%d</a><br>" % (cur_id, cur_id)

        template = tornado.template.Template('''
            <html>
                <body>
                    <a href="../menu"> Назад </a>
                    <br><br>
                    %s
                    <a href = '../sessions' class="hall">Sessions</a>
                </body>
            </html>
        ''' % halls_list)

        self.write(template.generate())

        connection.close()

class HallHandler(tornado.web.RequestHandler):
    def draw_table(self, table, hall_id):
        rows_num = len(table)
        cols_num = len(table[0])
        template = tornado.template.Template('''
            <html>
                <body>
                <a href="../menu"> Назад </a>
                <br><br>
                <table border="2">
                <caption>Зал № {{hall_id}} </caption>
                 <tr>
                    <td colspan="100" align="center">
                        <label> Экран </label>
                    </td>
                    {%for i in range(rows_num)%}
                        <tr>
                        <th>
                        <label> Ряд №{{i+1}} </label>
                        {%for j in range(cols_num)%}

                            {%if table[i][j] == -1%}
                                <td bgcolor="#fffff">
                                </td>
                            {%end%}
                            {%if table[i][j] == 0%}
                                <td bgcolor="#00ff00">
                                    <label> {{j+1}} </label>
                                </td>
                            {%end%}
                            {%if table[i][j] == 1%}
                                <td bgcolor="#ffcc00">
                                    <label> {{j+1}} </label>
                                </td>
                            {%end%}
                        {%end%}
                        </th>
                        </tr>
                    {%end%}
                </table>
                </body>
            </html>
        ''')
        self.write(template.generate(table = table, rows_num = rows_num, cols_num = cols_num, hall_id = hall_id))

    def get(self):
        hall_id = int(self.get_argument('id'))
        connection = sqlite3.connect('../data/cinema.db')
        sql_cursor = connection.cursor()

        rows_num = sql_cursor.execute('select rows_num from halls where hall_id = ?', (hall_id,)).fetchone()[0]
        cols_num = sql_cursor.execute('select chairs_num from halls where hall_id = ?', (hall_id,)).fetchone()[0]

        table = list([])
        for row in range(rows_num):
            hall_list = list([])
            for col in range(cols_num):
                res = sql_cursor.execute('select state from seats where hall_id=%d and row_id=%d + 1 and chair_id=%d + 1' % (hall_id, row, col)).fetchone()
                hall_list.append(res[0])
            table.append(hall_list)

        self.draw_table(table, hall_id)

        connection.close()

class SessionHandler(tornado.web.RequestHandler):
    def draw_table(self, table, halls, times):
        template = tornado.template.Template('''
            <html>
                <body>
                    <a href="../menu"> Назад </a>
                    <br><br>
                    <table border = "2">
                        <tr>
                            <td>
                            </td>
                            {%for time in times%}
                                <td> {{time[0]}} </td>
                            {%end%}
                        </tr>
                       {%for hall in halls %}
                        <tr>
                            <td> Зал №{{hall[0]}} </td>
                            {%for time in times %}
                                <td >
                                    <a href = ../hall?id={{hall[0]}}> {{table[hall[0]].get(time[0], " ")}}</a>
                                </td>
                            {%end %}
                        </tr>
                        {%end %}
                    </table>
                </body>
            </html>
        ''')
        self.write(template.generate(table = table, halls = halls,times = times))

    def get(self):
        connection = sqlite3.connect('../data/cinema.db')
        db_cursor = connection.cursor()

        halls = db_cursor.execute('select distinct hall_id from sessions order by hall_id').fetchall()
        times = db_cursor.execute('select distinct time from sessions order by time').fetchall()

        session_summary = db_cursor.execute('select time, film, hall_id from sessions').fetchall()
        table = {}
        for time, film, hall_id in session_summary:
            table.setdefault(hall_id,{})[time] = film

        self.draw_table(table, halls, times)

        connection.close()

if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/style.css", StylesHandler),
        (r"/", CinemaHandler),
        (r"/login", AuthoriseHandler),
        (r"/login_error", AuthoriseErrorHandler),
        (r".registration_error", RegistrationErrorHandler),
        (r"/menu", MenuHandler),
        (r"/films", FilmsHandler),
        (r"/halls", ChooseHandler),
        (r"/hall", HallHandler),
        (r"/sessions", SessionHandler)
    ])
    application.listen(8090)
    tornado.ioloop.IOLoop.instance().start()
