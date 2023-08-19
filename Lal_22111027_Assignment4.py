##Import VTK
from vtk import *
import random
import vtk
import numpy as np
import scipy.interpolate
import time

##Loading dataset

reader = vtkXMLImageDataReader() 
reader.SetFileName('Isabel_3D.vti') 
reader.Update() 
data = reader.GetOutput()
# print(data)

nOfPoints = data.GetNumberOfPoints()
#print(nOfPoints)
dataArr = data.GetPointData().GetArray('Pressure')
lst = []
for i in range(nOfPoints):
    s = dataArr.GetTuple1(i)
    lst.append(s)

def simpleRandomSampling(data, samplingPercentage):
    list = [0, 249, 62250, 62499, 3062500, 3062749, 3124750, 3124999]
    for i in range (int(nOfPoints*samplingPercentage)-8):
        index = random.randint(0, nOfPoints - 1)
        list.append(index)
        
       
    
    # Creating a new VTK polydata object 
    polyData = vtkPolyData()
    
    # Creating a points object
    points = vtkPoints()
    
    # Creating an array 
    dataValues = vtkFloatArray()
    dataValues.SetName("Data")
    
    for i in list:
        points.InsertNextPoint(data.GetPoint(i))
        dataValue = dataArr.GetTuple1(i)
        dataValues.InsertNextValue(dataValue)
        
    # Set the points and data array for the poly data object
    polyData.SetPoints(points)
    polyData.GetPointData().SetScalars(dataValues)
    # Write the sampled points to a VTKPolyData file
    writer = vtkXMLPolyDataWriter()
    writer.SetFileName('sampledPoints.vtp')
    writer.SetInputData(polyData)
    writer.Write()

    return polyData

samplingPercentage = int(input("Input Sampling percentage:"))
samplingPercentage *= 0.01
simpleRandomSampling(data, samplingPercentage)

method = input("Enter Method, nearest or linear :")

def reconstructVolume(data, method):
    # Loading the sampled point data from VTP file
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName('sampledPoints.vtp')
    reader.Update()
    data2 = reader.GetOutput()

    points = np.array([data2.GetPoint(i) for i in range(data2.GetNumberOfPoints())])
    values = np.array([data2.GetPointData().GetScalars().GetTuple1(i) for i in range(data2.GetNumberOfPoints())])

    # Define the grid points for the reconstruction
    grid_points = np.array([data.GetPoint(i) for i in range(data.GetNumberOfPoints())])

    startTime = time.time()

    # Reconstruct the volume using nearest interpolation
    volume_nearest = scipy.interpolate.griddata(points, values, grid_points, method=method)
    endTime = time.time()

    # Save the reconstructed volume as a VTK file

    volume_value = vtk.vtkFloatArray()
    for i in volume_nearest:
        volume_value.InsertNextValue(i)



    imageData = vtk.vtkImageData()
    imageData.SetDimensions(250,250,50)
    imageData.GetPointData().SetScalars(volume_value)
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName('reconstructed_volume_nearest.vti')

    writer.SetInputData(imageData)
    writer.Write()

    #computing SNR value
    arrgt = np.array(lst)
    arr_recon = np.array(volume_nearest)
    def compute_SNR(arrgt,arr_recon):
        diff =  arrgt - arr_recon
        sqd_max_diff = (np.max(arrgt) - np.min(arrgt))**2
        snr = 10*np.log10(sqd_max_diff/np.mean(diff**2))
        return snr
    snrValue = compute_SNR(arrgt, arr_recon)
    print(snrValue)
    print(endTime - startTime)
reconstructVolume(data,method)





