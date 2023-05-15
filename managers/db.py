from enum import Enum
import dotenv
import os

import psycopg2


class Method(Enum):
    SELECT = 1
    INSERT = 2
    UPDATE = 3
    DELETE = 4

    @staticmethod
    def get_str(method):
        if method == Method.SELECT:
            return 'SELECT'
        elif method == Method.INSERT:
            return 'INSERT'
        elif method == Method.UPDATE:
            return 'UPDATE'
        elif method == Method.DELETE:
            return 'DELETE'
        else:
            raise ValueError('가능한 method는 select:1, insert:2, update:3, delete:4, 입니다.')


class DBManager:
    """
    Select, Insert, Delete 하고자 하는 table의 데이터 관리 책임
    """
    connection = None
    request = None

    def __init__(self, host=None, name=None, user=None, port=None, password=None):
        dotenv_file = dotenv.find_dotenv()
        if dotenv_file:
            dotenv.load_dotenv(dotenv_file)

        if not host:
            host = os.environ['DB_HOST']
        self.host = host

        if not name:
            name = os.environ['DB_NAME']
        self.name = name

        if not user:
            user = os.environ['DB_USER']
        self.user = user

        if not port:
            port = os.environ['DB_PORT']
        self.port = port

        if not password:
            password = os.environ['DB_PASSWORD']
        self.password = password

        self._db_connect()

    def response(self, request):
        """
        :param request:
        Request 객체를 받음. 
        :return: 
        reqeust에 맞는 응답 해줌.
        """
        self.request = request
        query_str = self._get_query_str()
        cursor = self.connection.cursor()
        cursor.execute(query_str)
        if self.request.method == Method.SELECT:
            response = cursor.fetchall()
        else:
            response = None
        return response

    def _db_connect(self):
        connection_str = f'host={self.host} dbname={self.name} user={self.user} password={self.password} port={self.port}'
        connection = psycopg2.connect(connection_str)
        connection.autocommit = True
        self.connection = connection

    def _get_query_str(self):
        method_str = self._get_method_str()
        table_name_str = self._get_table_name_str()
        if self.request.method == Method.SELECT:
            column_str = self._get_column_str()
            query_str = f'{method_str} {column_str} FROM {table_name_str}'
        elif self.request.method == Method.UPDATE:
            column_set_value_str = self._get_column_set_value_str()
            query_str = f'{method_str} {table_name_str} SET {column_set_value_str}'
        elif self.request.method == Method.INSERT:
            column_str = self._get_column_str()
            value_str = self._get_value_str()
            query_str = f'{method_str} INTO {table_name_str} ({column_str}) VALUES ({value_str})'
        elif self.request.method == Method.DELETE:
            query_str = f'{method_str} FROM {table_name_str}'
        else:
            query_str = f'{method_str} FROM {table_name_str}'

        if self.request.filter_dict:
            filter_str = self._get_filter_str()
            query_str += f' WHERE {filter_str}'

        query_str += ';'

        return query_str

    def _get_method_str(self):
        return Method.get_str(self.request.method)

    def _get_table_name_str(self):
        return self.request.table_name

    def _get_column_str(self):
        # For select method
        if '__all__' in self.request.columns:
            return '*'
        else:
            return ','.join(self.request.columns)

    def _get_column_set_value_str(self):
        kv_str_list = []
        for key, value in self.request.set_columns_dict.items():
            value = str(value)
            kv_str = f'{key}={value}'
            kv_str_list.append(kv_str)

        return ','.join(kv_str_list)

    def _get_value_str(self):
        return ','.join(self.request.values)

    def _get_filter_str(self):
        if self.request.filter_dict:
            filter_kv_str_list = []
            for key, value in self.request.filter_dict.items():
                value = str(value)
                kv_str = f'{key}={value}'
                filter_kv_str_list.append(kv_str)
            return ' AND '.join(filter_kv_str_list)

        else:
            return ''


class Request:
    method = None
    # 컬럼명 list을 저장함
    columns = None
    # value list를 저장함
    values = None
    table_name = None
    set_columns_dict = {}
    filter_dict = {}

    # def __init__(self, table_name, columns=None, method=Method.SELECT):
    #     if method == Method.DELETE and columns != None:
    #         raise ValueError('DELETE Method는 columns를 가질 수 없습니다.')
    #     if columns is None:
    #         columns = ['__all__']
    #     self.method = method
    #     self.table_name = table_name
    #     self.columns = columns

    def select(self, table_name, columns=None):
        if columns is None:
            columns = ['__all__']
        self.method = Method.SELECT
        self.table_name = table_name
        self.columns = columns

        return self

    def update(self, table_name, **kwargs):
        if not kwargs:
            raise ValueError('column=value를 최소 하나 이상 설정해야 합니다.')
        self.method = Method.UPDATE
        self.table_name = table_name
        self.set_columns_dict = kwargs

        for k, v in kwargs.items():
            if type(v) == str:
                kwargs[k] = f"'{v}'"
            else:
                kwargs[k] = str(v)

        return self

    def insert(self, table_name, **kwargs):
        if not kwargs:
            raise ValueError('column=value를 최소 하나 이상 설정해야 합니다.')
        self.method = Method.INSERT
        self.table_name = table_name

        self.set_columns_dict = kwargs

        for k, v in kwargs.items():
            if type(v) == str:
                kwargs[k] = f"'{v}'"
            else:
                kwargs[k] = str(v)

        self.columns = kwargs.keys()
        self.values = kwargs.values()

        return self

    def delete(self, table_name):
        self.method = Method.DELETE
        self.table_name = table_name

        return self

    def filter(self, **kwargs):
        """
        Equal과 And를 지원합니다.
        :param kwargs:
        db에서 조회하고자하는 query명
        :return:
        """

        if self.method == Method.INSERT:
            raise ValueError(f'INSERT 메소드는 filter를 수행할 수 없습니다.')

        if kwargs:
            kwargs_clean = {}
            for k, v in kwargs.items():
                k_clean = k.replace('__', '.')
                if type(v) == str:
                    if '__' in v:
                        v_clean = v.replace('__', '.')
                    else:
                        v_clean = f"{v}"
                    kwargs[k] = v_clean

                kwargs_clean[k_clean] = kwargs[k]
            self.filter_dict = kwargs_clean
        return self

