import pandas
import numpy
import openpyxl
import xlrd
import dotenv
import sqlalchemy

def test_environment():
    assert pandas.__version__
    assert numpy.__version__
    assert openpyxl.__version__
    assert xlrd.__version__
    assert sqlalchemy.__version__