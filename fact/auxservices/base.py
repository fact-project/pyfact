from astropy.table import Table
from astropy.units import UnitsWarning
import os
import warnings


class AuxService:

    renames = {}
    ignored_columns = []
    transforms = {}
    basename = 'AUX_SERVICE'

    def __init__(self, auxdir='/fact/aux'):
        self.auxdir = auxdir

    @property
    def filename_template(self):
        return os.path.join(
            self.auxdir, '{date:%Y}',  '{date:%m}', '{date:%d}',
            '{date:%Y%m%d}.' + self.basename + '.fits'
        )

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

        filename = self.filename_template.format(date=date)
        return self.read_file(filename)
