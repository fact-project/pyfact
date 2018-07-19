import pkgutil
import yaml

import os.path
from .models import RunInfo, Source, RunType

def create_default_query():
    """
    Creates the default query that one would use with the fact data.
    Which is basically just the RunInfo with the source/runtype as a name and not just the number.
    """
    query = (RunInfo.select()
            .join(Source, on=(Source.fsourcekey == RunInfo.fsourcekey))
            .join(RunType, on=RunType.fruntypekey == RunInfo.fruntypekey)
            )
    return query

def create_condition_set(conditionset=['@standard']):
    """
    given a list of conditions create a condition set
    
    If a given condition start with '@NAME', process NAME as a set of conditions defined in a yaml file
    with the filename NAME or with the 
    """
    data_conditions = []
    for condition in conditionset:
        if condition.startswith('@'):
            # check if file exists
            fname = condition[1:]
            if os.path.isfile(fname):
                with open(fname, 'r') as f:
                    config = yaml.safe_load(f)
                    more_conditions = config['conditions']
            else:
                data = None
                if fname.endswith('.yaml'):
                    data = pkgutil.get_data('fact_conditions', 'conditions/'+fname)
                else:
                    data = pkgutil.get_data('fact_conditions', 'conditions/'+fname+'.yaml')
                if data is None:
                    raise ValueError("The given condition file: '{}' does not exist".format(fname))
                try:
                    config = yaml.safe_load(data)
                except:
                    print("ERROR: Something went wrong in the yaml file from '{}'".format(fname))
                    raise
                more_conditions = config['conditions']
            data_conditions = data_conditions + more_conditions
        else:
            data_conditions.append(condition)
    return data_conditions

from peewee import SQL
def apply_to_query(query, conditionSets):
    """
    Given a peewee query, creates the final condition set with create_condition_set from the given sets
    and applies them to the query.
    """
    if type(conditionSets) is str:
        conditionSets = [conditionSets]
    conditionSet = create_condition_set(conditionSets)
    for c in conditionSet:
        query = query.where(SQL(c))
    return query
    
def create_query_apply_cond(conditionSets):
    """
    Creates a default query and applies the given condition sets
    """
    query = create_default_query()
    apply_to_query(query, conditionSets)
    return query
