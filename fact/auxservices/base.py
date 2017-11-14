from astropy.table import Table
from astropy.units import UnitsWarning
from ..path import tree_path
from functools import partial
import warnings


class AuxService:

    renames = {}
    ignored_columns = []
    transforms = {}
    basename = 'AUX_SERVICE'

    def __init__(self, auxdir='/fact/aux'):
        self.path = partial(
            tree_path,
            run=None,
            prefix=auxdir,
            suffix='.' + self.basename + '.fits')

    @classmethod
    def read_file(cls, filename):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=UnitsWarning)
            table = Table.read(filename)

        for column in table.columns.keys():
            if column in cls.ignored_columns:
                table.remove_column(column)

            elif column in cls.renames:
                table[column].name = cls.renames[column]

        for column in table.columns.keys():
            shape = table[column].shape
            if len(shape) > 1:
                for i in range(shape[1]):
                    table[column + '_{}'.format(i)] = table[column][:, i]
                table.remove_column(column)

        df = table.to_pandas()

        for key, transform in cls.transforms.items():
            df[key] = transform(df[key])

        return df

    def read_date(self, date):
        return self.read_file(self.path(int('{:%Y%m%d}'.format(date))))
