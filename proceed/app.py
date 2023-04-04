import flask
import os
import lexana
import lr1

app = flask.Flask(__name__, static_folder="../static/",
                  static_url_path="", template_folder="../static/")


def root_dir():  # pragma: no cover
    dirpath = os.path.dirname(__file__)
    return os.path.join(os.path.split(dirpath)[0])


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir()+'\\\\txt', filename)
        return src
    except IOError as exc:
        return str(exc)


@app.route('/')
def index():
    return flask.render_template('homepage.html')


@app.route('/upload_file', methods=["POST"])
def upload_file():
    file1 = flask.request.form.get('lexical')
    file2 = flask.request.form.get('code')
    file3 = flask.request.form.get('grammar')
    args = {'file1_flag': 'failed',
            'file2_flag': 'failed',
            'file3_flag': 'failed',
            'token_list': [],
            'warning_list': [],
            'parser_table': [],
            'pstklist': [],
            'statestklist': []}
    if file1 is not None:
        args['file1_flag'] = 'success'
    if file2 is not None:
        args['file2_flag'] = 'success'
    if file3 is not None:
        args['file3_flag'] = 'success'
    lexical_dir = get_file(file1)
    code_dir = get_file(file2)
    grammar_dir = get_file(file3)
    lexparser = lexana.PARSER(lexical_dir, code_dir)
    grammarparser = lr1.PARSER(grammar_dir)
    parsertable = grammarparser.lr1.parsertablelist()
    token_list, warning_list = lexparser.parse()
    grammar_result, pstklist, statestklist = grammarparser.parse(token_list)
    f = open("{}\\result\\tokens.txt".format(root_dir()), "w+")
    f.write(str(token_list))
    f.close()
    f = open("{}\\result\\grammar_result.txt".format(root_dir()), "w+")
    f.write(str(grammar_result))
    f.close()
    f = open("{}\\result\\pstklist.txt".format(root_dir()), "w+")
    f.write(str(pstklist))
    f.close()
    f = open("{}\\result\\statestklist.txt".format(root_dir()), "w+")
    f.write(str(statestklist))
    f.close()
    args['token_list'] = token_list
    args['warning_list'] = warning_list
    args['parser_table'] = parsertable
    args['grammar_result'] = grammar_result
    args['pstklist'] = pstklist
    args['statestklist'] = statestklist
    return flask.render_template('homepage.html', **args)


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


def main():
    app.run()


if __name__ == "__main__":
    main()
