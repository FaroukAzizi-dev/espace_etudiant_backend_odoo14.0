# Load base/independent models first
from . import evaluationtype
from . import programme
from . import filiere
from . import niveau
from . import matiere
# Then load user-related models
from . import etudiant
from . import enseignant
from . import parent

# Then load dependent models
from . import classe  # Depends on filiere, niveau, enseignant
from . import edt     # Depends on classe, matiere, etc.
from . import note
from . import absence
from . import reclamation
from . import reclamation_prof
from . import document