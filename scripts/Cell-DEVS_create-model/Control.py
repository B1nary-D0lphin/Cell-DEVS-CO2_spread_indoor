# Class which controls the flow of the program
# Thomas Roller

import sys
import json
from ImageTools import ImageTools
from ConvertTools import ConvertTools
from GeneralTools import GeneralTools

class Control:

    @staticmethod
    def start (args):
        # Get configuration filename
        configFile = "config.json"
        if (args.config is not None):
            configFile = args.config

        config = ""
        try:
            # Load configuration from file
            with open(configFile, "r") as f:
                config = f.read()
        except FileNotFoundError:
            print("ERROR: Could not load configuation file")
            sys.exit(1)

        config = json.loads(config)  # Convert JSON string into dictionary

        model = None
        convertType = Control.convertType(config["files"], args.dim)
        # Input model is an image with matching dimensions
        if (convertType == "exact_image"):
            model = Control.exactImageParse(config)
        # Input model is an image with mismatched dimensions (guessing required)
        elif (convertType == "extrapolate_image"):
            return  # will include processing where image size and shape do not match
        # Input model is a JSON
        elif (convertType == "json"):
            model = Control.json_2Dto3D(config)

        # Export the JSON string
        GeneralTools.export(config["files"]["output"], ConvertTools.getString(model))

    # Get the extension of a file
    @staticmethod
    def getExtension (filename):
        loc = filename.find(".")
        if (loc < 0 or loc >= len(filename) - 1):
            return None
        return filename[loc + 1:].lower()

    # Determine what type of conversion to perform
    @staticmethod
    def convertType (files, outDim):
        imageFormats = ["bmp", "jpg", "jpeg", "png"]
        extension = Control.getExtension(files["input"])
        # If there is no extension
        if (extension == None):
            return None
        # If the extension indicates an image
        elif (extension in imageFormats):
            imageDim = ImageTools.getDimensions(files["input"])
            # If the user did not provide a specific output dimension (no error due to short-circuit evaluation)
            if (outDim == None or (imageDim[0] == outDim[0] and imageDim[1] == outDim[1])):
                return "exact_image"
            # If the user provided a specific output dimension
            else:
                return "extrapolate_image"
        # If the extension indicates a JSON
        elif (extension == "json"):
            return "json"

    # Convert image files to 2D or 3D formatted models (depending on configuration file)
    @staticmethod
    def process_exactImage (config):
        image = ImageTools(config)  # Prepare the image tools
        image.load()                # Load the image
        cells = image.makeCells()   # Make cells out of the image

        # Generate the head of the model
        head = ConvertTools.createHead(image.getWidth(), image.getLength(), config["model"])

        # If the model is 3D, extend the walls and add a floor and ceiling
        if (config["model"]["height"] > 1):
            cells = ConvertTools.getExtendedCells(config["model"], cells)
            cells = ConvertTools.addFloorCeiling(image.getWidth(), image.getLength(), config["model"]["height"], cells)

        return ConvertTools.createStructure(head, cells)  # Combine the head and the cells

    # Convert 2D JSON formatted models to 3D JSON formatted models
    @staticmethod
    def process_json_2Dto3D (config):
        # Get 2D JSON
        data = ""
        try:
            # Load configuration from file
            with open(config["files"]["input"], "r") as f:
                data = f.read()
        except FileNotFoundError:
            print("ERROR: Could not load input file")
            sys.exit(1)

        data = json.loads(data)  # Convert JSON string into dictionary

        width, length = data["scenario"]["shape"][0], data["scenario"]["shape"][1]

        # Generate the head of the model
        head = ConvertTools.createHead(width, length, config["model"])

        # Extract the cells
        cells = data["cells"]

        # If the model is 3D, extend the walls and add a floor and ceiling
        if (config["model"]["height"] > 1):
            cells = ConvertTools.getExtendedCells(config["model"], cells)
            cells = ConvertTools.addFloorCeiling(width, length, config["model"]["height"], cells)

        return ConvertTools.createStructure(head, cells)  # Combine the head and the cells

    # Convert
    @staticmethod
    def process_inexactImage (config, outDim):
        print("NOTE: Image dimensions do not match provided dimensions (inexact image processing will take place)")
        print("ERROR: Feature not yet implemented")
        return  # will be removed when function implentation is complete

        image = ImageTools(config)  # Prepare the image tools
        image.load()                # Load the image