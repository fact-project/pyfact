import click
import yaml
from .conditions import create_condition_set

@click.command()
@click.option('--condition', '-c', multiple=True, help='Only use events that fullfill this condition type')
@click.option('--author', help="The author of the condition set")
@click.option('--description', help="The description of the dataset")
@click.option('--name', help="The name of the condition set")
@click.option('--firstnight', help="The first night to consider")
@click.option('--lastnight', help="the last night to consider")
@click.option('--source', help="Set the source to use, only works if RunInfo is merged with Source.")
@click.argument('outfile', type=click.Path(exists=False, dir_okay=False, file_okay=True, readable=True) )
def main(condition, outfile, author, description, name, firstnight, lastnight, source):
    """
    Creates a new conditionset with the given conditons/conditionSets.
    """
    print("Load condition set")
    conditionSet = create_condition_set(condition)
    
    if firstnight:
        conditionSet.append("fNight >= {}".format(firstnight))
    if lastnight:
        conditionSet.append("fNight <= {}".format(lastnight))
    
    if source:
        conditionSet.append("fSourceName = '{}'".format(source))
        
    config = {
        'name': name,
        'author': author,
        'description': description,
        'conditions': conditionSet
    }
    
    print("Create new condition file")
    with open(outfile, 'w') as yaml_file:
        yaml.dump(config, yaml_file, default_flow_style=False)
    print("Finished")


if __name__ == '__main__':
    main()