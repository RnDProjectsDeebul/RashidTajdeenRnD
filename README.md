# RashidTajdeenRnD

## Introduction

Though Deep Neural Networks (DNNs) are being used extensively in many fields including safety critical systems such as autonomous driving and medical diagnostics, there are chances for the DNN to exhibit erroneous behaviours.

Testing a DNN is not that feasible as classical software testing. In a classical software, we know whats happening at every point of time. When you have a problem, you exactly know where it occurs and how to rectify them. Hence we would use white-box testing which touches the internals of the software. But in a AI software, testing the software internals is of no use. After a model is trained, we have no clue whats happening inside all those networks, it just happens. Hence the best option is to follow the black-box testing approach in which we test the functionality of the software from the outside.

### Goal of this RnD

The goal of this RnD is to test deep neural networks. The focus is not on testing the performance of a deep neural network, instead to test its capability. To aid this testing, we use behaviour driven development methods which takes in both requirements from test engineers and the capabilities of blender thereby generating synthetic test dataset in blender for testing the learned DNN models.

![basic block](https://user-images.githubusercontent.com/47964895/173790350-5e958957-a0e6-4e35-b38f-83a349872a9e.png)

### Why is it essential to test a DNN?

- The most verified process of testing deep neural networks is to use test datasets. This aspect of testing is more viable and trusted than the other aspects of testing.
- In most DNN image classifiers, the trained models misunderstands one class with the other, or even sometimes show one-sided biases. Hence the properties of the class are violated and misinterpreted.
- Some DNNs perform well on simple tasks, but when it comes to the point to expand its use case, the user might begin to face capability issues from the model.
- We could never say a DNN model is perfectly trained and can perform well on any situation, because the possibilities real world inputs to this model is infinite.

## Preparations

- Clone the repository to the local machine.
- The user must have the latest version of blender installed in the machine.
- Download the input data from the [here][input_zip], extract it and place the extracted input folder in the root of the repository

## Working

##### Dataset generation
The control starts with the src/main.cpp file where the blender application is started given a bpy script. Inside the bpy script, the entire model creation and alteration process is carried out. This script uses the functions from src/bpy_functions.py. Models to be imported in blender are inside input folder.

##### Training the model
The input folder contains the dataset with images and the ground truth csv. Training uses this data to train the model and gives out model.pth to the output folder.

##### Validating the model
The model.pth is validated with a new set of data and the output is stored in the output folder.


## Usage

To generate dataset, use the command
```console
make dataset
```

To train the model, use the command
```console
make train
```

To validate the model, use the command
```console
make validate
```

To run the BDD tests, use the command
```console
make test
```


[input_zip]: https://drive.google.com/file/d/17NgwN_2PqS7OiDDve0oA6NBsZEN0sNVv/view?usp=sharing
