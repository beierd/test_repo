import hptestbench

# Wärmepumpen installieren
HP_nf = hptestbench.testbench()
HP_alba = hptestbench.testbench()
HP_vc = hptestbench.testbench()

HP_alba.install_HP('Q100_air_water_001')
HP_nf.install_HP('NibeFighter1140_15')
HP_vc.install_HP('Vitocal350AWI114')

# Vorlauftemperaturen setzen
HP_vc.parameters["T_cond_in.k"] = 273.15 + 40 # Luft-WP
HP_nf.parameters["T_cond_in.k"] = 273.15 + 40 # Erdwärmepumpe
HP_alba.parameters["T_cond_in.k"] = 273.15 + 70
HP_alba.stepSize = 3600

HP_alba.test_with_modelica(make_FMU=False) #Erstellen der FMU funktioniert
HP_nf.test_with_modelica(make_FMU=False) #Erstellen der FMU funktioniert
HP_vc.test_with_modelica(make_FMU=False) #Erstellen der FMU funktioniert




# Mögliche Wärmepumpen
#'AlphaInnotec_SW170I'
#'Vitocal350AWI114' 18,5 kW Nennwwärmeleistung, Luft-WP
# 'Vitocal350BHW113', 17,7 kW Nennwärmeleistung, Sole/Wasser WP 
# 'Vitocal350BHW110'
#'NibeFighter1140_15'
# EN14511 Ordner
#'AlphaInnotec_LW80MA'
#'Ochsner_GLMW_19'
#'Ochsner_GMSW_15Plus'
#'Vaillant_VWL_101'
#'Dimplex_LA11AS'
#'Ochsner_GLMW_19plus'
#'StiebelEltron_WPL18'


# Wiederholen der Simulation mittels FMU
#HP.test_with_FMU()


HP_alba.evaluate()
HP_nf.evaluate()
HP_vc.evaluate()

COP_alba = HP_alba.data['heatPump1.CoP_out']
COP_nf = HP_nf.data['heatPump1.CoP_out']
COP_vc = HP_vc.data['heatPump1.CoP_out']