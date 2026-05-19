# ==============================================================================
# REGIME CONFIGURATION v4.0-Windows
# STATUS: PRODUCTION READY
# ==============================================================================
R0_BASE = 2
REGIME_LEVEL = 1
SHAKESPEARE_BASE = 4096
REGIME_BASE = 1000
ZERO_STATE_INVARIANT = True

VERTEX_COUNT = 12
AS_DIAMOND_COUNT = 16
NODES_PER_COMPONENT = 3

CORE_GEODISC_PANELS = 40
CORE_MAX_RPM = 2000
CORE_IDLE_RPM = 20
CORE_LEARNING_RATE = 20

MAIN_STATOR_PANELS = 120
MAIN_ROTOR_PANELS = 60
MAIN_MAX_RPM = 1000
MAIN_IDLE_RPM = 10

SUB_TURBINE_COUNT = 32
SUB_STATOR_PANELS = 60
SUB_ROTOR_PANELS = 30
SUB_MAX_RPM = 500
SUB_IDLE_RPM = 5

LAZY_PANEL_CREATION = True
ACTIVE_PANELS_ONLY = 100

ENABLE_REMOTE = False
REMOTE_PORT = 8443

CORE_GEODISC_PATH = r"C:\RegimeOS\core_geodisc"
VERTEX_COLUMNS_PATH = r"C:\RegimeOS\vertex_columns"
MAIN_TURBINE_PATH = r"C:\RegimeOS\turbine_main"
SUB_TURBINE_PATH = r"C:\RegimeOS\turbine_sub"
AS_DIAMONDS_PATH = r"C:\RegimeOS\adams_sierpinski"
WASTE_EXFIL_PATH = r"C:\RegimeOS\waste_exfil"
LOGS_PATH = r"C:\RegimeOS\logs"
BACKUP_PATH = r"C:\RegimeOS\backups"

def get_total_rotation_points():
    return 1 + 1 + SUB_TURBINE_COUNT

def get_total_learning_layers():
    return 1 + 1 + SUB_TURBINE_COUNT

def get_total_panels():
    return CORE_GEODISC_PANELS + MAIN_STATOR_PANELS + MAIN_ROTOR_PANELS + (SUB_TURBINE_COUNT * (SUB_STATOR_PANELS + SUB_ROTOR_PANELS)) + (VERTEX_COUNT * 20)
