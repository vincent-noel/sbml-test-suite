
from libsedml import SedDocument, writeSedMLToFile, parseFormula
from libsbml import SBMLReader, ConversionProperties, Species, Parameter, Compartment, Reaction

from os import listdir
from os.path import isfile, isdir, join, dirname, abspath, exists, basename
from glob import glob
from re import match


def setTarget(sbml_model, variable, sbml_variable):
	
	xpath = ""
	if isinstance(sbml_variable, Species):
		xpath = "/sbml:sbml/sbml:model/sbml:listOfSpecies/sbml:species"
	elif isinstance(sbml_variable, Parameter):
		xpath = "/sbml:sbml/sbml:model/sbml:listOfParameters/sbml:parameter"
	elif isinstance(sbml_variable, Compartment):
		xpath = "/sbml:sbml/sbml:model/sbml:listOfCompartments/sbml:compartment"
	elif isinstance(sbml_variable, Reaction):
		xpath = "/sbml:sbml/sbml:model/sbml:listOfReactions/sbml:reaction"
	else:
		print(type(sbml_variable))
		raise Exception()

	idref = ""
	if sbml_model.getLevel() == 1:
		idref = "[@name='%s']" % variable
	else:
		idref = "[@id='%s']" % variable

	return xpath+idref

TEST_FILES = join(dirname(dirname(dirname(dirname(__file__)))), "cases", "semantic")


for test_case in sorted(listdir(TEST_FILES)):

	dir = join(TEST_FILES, test_case)

	if not isfile(dir) and test_case != ".":
		print("\n> %s : " % test_case)

		versions = []
		for sbml_file in glob("%s/*-sbml-*.xml" % dir):
			res_match = match(r"%s/%s-sbml-l(\d+)v(\d+).xml" % (dir, test_case), sbml_file)
			if res_match != None:
				versions.append((int(res_match.groups()[0]), int(res_match.groups()[1])))

		settings_file = open(join(dir, "%s-settings.txt" % test_case), 'r')

		start = None
		duration = None
		steps = None
		variables = []
		amount = []
		concentration = []
		for line in settings_file.readlines():
			if ":" in line:

				str = (line.split(":")[1]).strip()
				if str != "":
					if line.startswith("start:"):
						start = float(str)

					if line.startswith("duration:"):
						duration = float(str)

					if line.startswith("steps:"):
						steps = int(str)

					if line.startswith("variables:"):
						variables = [variable.strip() for variable in str.split(",")]

					if line.startswith("amount:"):
						amount = [variable.strip() for variable in str.split(",")]

					if line.startswith("concentration:"):
						concentration = [variable.strip() for variable in str.split(",")]
		if start != None and duration != None and steps != None:

			for level, version in sorted(versions):

				sbml_filename = join(dir, "%s-sbml-l%dv%d.xml" % (test_case, level, version))
				print(sbml_filename)
				sbmlReader = SBMLReader()
				sbml_doc = sbmlReader.readSBML(sbml_filename)
				sbml_model = None

				if sbml_doc.getLevel() == 3 and sbml_doc.isSetPackageRequired("comp"):
					props = ConversionProperties()
					props.addOption('flatten comp', True)  # Invokes CompFlatteningConverter
					sbml_doc.convert(props)
					sbml_model = sbml_doc.getModel()

				elif sbml_doc.getLevel() == 3 and sbml_doc.isSetPackageRequired("fbc"):
					pass

				else:
					sbml_model = sbml_doc.getModel()

				if sbml_model is not None:

					sedml_filename = join(dir, "%s-sbml-l%dv%d-sedml.xml" % (test_case, level, version))

					sedml_doc_v2 = SedDocument()

					simulation = sedml_doc_v2.createUniformTimeCourse()
					simulation.setId("simulation")
					simulation.setInitialTime(start)
					simulation.setOutputStartTime(start)
					simulation.setOutputEndTime(duration)
					simulation.setNumberOfPoints(steps)

					algo = simulation.createAlgorithm()
					algo.setKisaoID("KISAO:0000019")

					model = sedml_doc_v2.createModel()
					model.setId("model")
					model.setLanguage("urn:sedml:language:sbml")
					model.setSource(basename(sbml_filename))

					task = sedml_doc_v2.createTask()
					task.setId("task")
					task.setModelReference("model")
					task.setSimulationReference("simulation")

					data_time = sedml_doc_v2.createDataGenerator()
					data_time.setId("data_generator_time")
					data_time.setName("time")
					var_time = data_time.createVariable()
					var_time.setId("time")
					var_time.setSymbol("urn:sedml:symbol:time")
					var_time.setModelReference("model")
					var_time.setTaskReference("task")
					math_time = parseFormula("time")
					data_time.setMath(math_time)

					if not sbml_model.isPopulatedAllElementIdList():
						sbml_model.populateAllElementIdList()

					data_variables = []

					id_list = sbml_model.getAllElementIdList()
					model_variables = [id_list.at(ind_id) for ind_id in range(id_list.size())]
					for i, variable in enumerate(variables):

						if variable in model_variables:
							sbml_variable = sbml_model.getElementBySId(variable)
							data_variable = sedml_doc_v2.createDataGenerator()
							data_variable.setId("data_generator_variable_%d" % i)
							data_variable.setName(variable)

							# Three cases :
							# - variable is a concentration, and we want the amount
							if isinstance(sbml_variable, Species) and not sbml_variable.getHasOnlySubstanceUnits() and variable in amount:
								var_variable = data_variable.createVariable()
								var_variable.setId(variable)
								var_variable.setTaskReference("task")
								var_variable.setModelReference("model")
								var_variable.setTarget(setTarget(sbml_model, variable, sbml_variable))
								var_compartment = data_variable.createVariable()
								var_compartment.setId(sbml_variable.getCompartment())
								var_compartment.setTaskReference("task")
								var_compartment.setModelReference("model")
								compartment = sbml_model.getElementBySId(sbml_variable.getCompartment())
								var_compartment.setTarget(setTarget(sbml_model, sbml_variable.getCompartment(), compartment))
								data_variable.setMath(parseFormula(variable + "*" + sbml_variable.getCompartment()))

							# - variable is an amount, anf we want a concentration
							elif isinstance(sbml_variable, Species) and sbml_variable.getHasOnlySubstanceUnits() and variable in concentration:
								var_variable = data_variable.createVariable()
								var_variable.setId(variable)
								var_variable.setTaskReference("task")
								var_variable.setModelReference("model")
								var_variable.setTarget(setTarget(sbml_model, variable, sbml_variable))
								var_compartment = data_variable.createVariable()
								var_compartment.setId(sbml_variable.getCompartment())
								var_compartment.setTaskReference("task")
								var_compartment.setModelReference("model")
								compartment = sbml_model.getElementBySId(sbml_variable.getCompartment())
								var_compartment.setTarget(setTarget(sbml_model, sbml_variable.getCompartment(), compartment))
								data_variable.setMath(parseFormula(variable + "/" + sbml_variable.getCompartment()))

							# - variable is what we want
							else:
								var_variable = data_variable.createVariable()
								var_variable.setId(variable)
								var_variable.setTaskReference("task")
								var_variable.setModelReference("model")
								var_variable.setTarget(setTarget(sbml_model, variable, sbml_variable))
								data_variable.setMath(parseFormula(variable))

					report = sedml_doc_v2.createReport()
					report.setId("report")
					dataset_time = report.createDataSet()
					dataset_time.setId("report_dataset_time")
					dataset_time.setDataReference("data_generator_time")
					dataset_time.setLabel("Time")

					for i, variable in enumerate(variables):
						dataset_variable = report.createDataSet()
						dataset_variable.setId("report_dataset_variable_%d" % i)
						dataset_variable.setDataReference("data_generator_variable_%d" % i)
						dataset_variable.setLabel(variable)

					sedml_filename = join(dir, "%s-sbml-l%dv%d-sedml.xml" % (test_case, level, version))
					writeSedMLToFile(sedml_doc_v2, sedml_filename)

