import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3

class StylesHandler(tornado.web.RequestHandler):
    def get(self):
        template = tornado.template.Template('''
            .table_header{
                text-decoration: underline;
                text-transform: capitalize;
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
            .ticket{
                font-family: fantasy;
                font-size: 28px;
                font-style: oblique;
                word-spacing: 2px;
                padding: 4px;
                color:#5088ed;
            }
            .hall{
                height: 25px;
                width: 25px;
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
        if action == "Вход":
            query = "SELECT login, password FROM users"
            db_cursor.execute(query)
            user_base = db_cursor.fetchall()
            if (login, password) in user_base:
                self.set_cookie("user", login)
                self.redirect('../menu')
            else:
                self.redirect('../login_error')
        else:
            query = ("INSERT INTO USERS (login, password) VALUES('"+login+"', '"+password+"')")
            db_cursor.execute(query)
            self.set_cookie("user", login)
            db_cursor = connection.cursor()
            query = ("INSERT INTO TICKETS (login, purchase_num) VALUES('"+login+"', 0)")
            db_cursor.execute(query)
            connection.commit()
            self.redirect('../menu')

class AuthoriseErrorHandler(tornado.web.RequestHandler):
    def get(self):
        template = tornado.template.Template('''
            <html>
                <head>
                    <title> Error </title>
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
                        <!-- <br><a href="../tickets"> Купить билет </a><br> -->
                    </center>
                </body>
            </html>
        ''')
        self.write(template.generate())

class FilmsHandler(tornado.web.RequestHandler):
    def get(self):
        connection = sqlite3.connect('../data/cinema.db')
        db_cursor = connection.cursor()
        query = "select * from films"
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

class ChooseHandler(tornado.web.RequestHandler):
    def get(self):
        connection = sqlite3.connect('../data/cinema.db')
        db_cursor = connection.cursor()
        halls = db_cursor.execute("select hall_id from halls").fetchall()

        halls_list = ""
        for hall_id in halls:
            cur_id = hall_id[0]
            halls_list += "<a href = '../hall?hall_id=%d'>Зал #%d</a><br>" % (cur_id, cur_id)

        template = tornado.template.Template('''
            <html>
                <body>
                    %s
                    <a href = '../sessions'>Sessions</a>
                </body>
            </html>
        ''' % halls_list)
        self.write(template.generate())

class HallHandler(tornado.web.RequestHandler):
    def draw_table(self, table, hall_id):
        table_code = "<html><body><header>Hall %d </header>" % hall_id
        table_code += '<table style="table-layout: fixed">'
        for row in table:
            table_code += '<tr>'
            for elem in row:
                table_code += '<td>' + str(elem) + '</td>'
            table_code += '</tr>'

        table_code += "</table></body></html>"
        self.write(table_code)

    def get(self):
        hall_id = int(self.get_argument('hall_id'))
        connection = sqlite3.connect('../data/cinema.db')
        sql_cursor = connection.cursor()

        rows_num = sql_cursor.execute('select rows_num from halls where hall_id = ?', (hall_id,)).fetchone()[0]
        cols_num = sql_cursor.execute('select chairs_num from halls where hall_id = ?', (hall_id,)).fetchone()[0]

        table = list([])

        for row in range(rows_num):
            hall_list = list([])
            for col in range(cols_num):
                res = sql_cursor.execute('select state from seats where hall_id=%d and row_id=%d + 1 and chair_id=%d + 1' % (hall_id, row, col)).fetchone()
                hall_list.append(res)
            table.append(hall_list)

        self.draw_table(table, hall_id)

        connection.close()

class SessionHandler(tornado.web.RequestHandler):
    def draw_table(self, table):
        table_code = "<html><body><header>Сегодняшние сеансы</header>"
        table_code += '<table style="table-layout: fixed">'
        for row in table:
            table_code += '<tr>'
            for elem in row:
                table_code += '<td>' + str(elem) + '</td>'
            table_code += '</tr>'

        table_code += "</table>"
        table_code += "</body></html>"
        self.write(table_code)

    def get(self):
        connection = sqlite3.connect('../data/cinema.db')
        db_cursor = connection.cursor()

        first_line = ['# зала']
        times = db_cursor.execute('select distinct time from sessions order by time').fetchall()
        for time in times:
            first_line.append(str(time[0]))

        table = list([first_line])

        halls = db_cursor.execute('select distinct hall_id from sessions order by hall_id').fetchall()

        for hall in halls:
            sessions = db_cursor.execute('select film, time from sessions where hall_id = %d order by time' % hall[0]).fetchall()

            hall_list = list([])

            len_line = len(first_line)
            for session in sessions:
                time, film = session[1], session[0]
                place = 1
                while place < len_line:
                    if first_line[place] == time:
                        hall_list.append(film)
                        place += 1
                    else:
                        place += 1
                        hall_list.append("* NONE *")

            table.append(["Зал %d" % hall[0]] + hall_list)

        self.draw_table(table)

        connection.close()

if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/style.css", StylesHandler),
        (r"/", CinemaHandler),
        (r"/login", AuthoriseHandler),
        (r"/login_error", AuthoriseErrorHandler),
        (r"/menu", MenuHandler),
        (r"/films", FilmsHandler),
        (r"/halls", ChooseHandler),
        (r"/hall", HallHandler),
        (r"/sessions", SessionHandler)
    ])
    application.listen(8090)
    tornado.ioloop.IOLoop.instance().start()
