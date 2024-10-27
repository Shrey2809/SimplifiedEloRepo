from sqlalchemy.ext.automap import automap_base
from .database import engine

# Reflect the database tables
Base = automap_base()
Base.prepare(engine, reflect=True)

Pickems = Base.classes.Pickems