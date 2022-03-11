# Design document

## General vision

LogicLayer is thought as a framework to implement advanced calculations for the use on frontend. The source of the data for these calculation can come from OLAP cubes (tesseract, mondrian), databases, static files, or any other kind of source, while the processing is done using specialized libraries like numpy, pandas, fbprophet, tensorflow, geopandas, and the like. This is the main motive to refactor the code from the different frameworks we were using to python. This library should also be scalable horizontally, to be prepared for deployment on Kubernetes/EC2 instances if needed.

As a framework, the main function is supply the tools to ease the connection between the datasources and the processing libraries, while providing the ability to output the results in a format useable for our platforms. It should also be prepared to catch and report runtime errors, so our developers are able to quickly address any kind of problem, be caused by issues with the data or with the calculations.

The core LogicLayer project should not implement neither datasource connections nor processing libraries (hereby "calculations") by itself. The calculations should be supplied as extension modules, and implemented following the instructions, and using the tools, provided by the core LogicLayer project. The project where LogicLayer is deployed should be responsible of the installation and implementation of the calculation modules, so only the required functionality is available.

As an example, a LogicLayer module for economic complexity might depend on the core LogicLayer modules that can retrieve the data from tesseract-olap, convert that data into a pandas dataframe, pass the dataframe into a module with functions that calculate economic complexity, and return these results to the user as JSON. The core LogicLayer framework should make sure every part is executed successfully, or/and report any exception raised during execution.

## Code Guidelines

These are the base guidelines to write modules for this app. These guidelines are required to consider a module ready for production.

A module prototype can ignore some of them during development to allow quick iterations, but should not be allowed on production until all the guidelines are correctly applied.

### Data processing

Since we could need any kind of data processing library not only on the module is intended for, but in multiple modules or even new services in the future, data processing functions should be as framework-agnostic as possible. Depending on numpy or maybe pandas is allowed.
It's ok to pack these functions on their own modules if there's an assumption it can be reused by other modules in the future.

- All data processing functions should accomplish the minimum objective possible.
- The parameters passed to these functions must be only primitives and data structures, and should not be related to the web framework.
- All functions must be documented appropiately, including type, shape, and expected return. This is a library that relies heavily on academic knowledge, and not all developers may be familiar with the theory.
- All functions should also raise Exceptions if there's a deviation of the normal behavior, eg. if the parameters don't have the same size. Remember to document the Exceptions created for this purpose.
- If other libraries or some parts of the code can raise their own exceptions, catch them only if they're relevant to the internals of the function they're contained in. When catching exceptions, try to be as specific as possible. DO NOT catch using `Exception`.
- All functions should be have their own test suites. The tests should attempt both to reach successful returns, and raise intended exceptions.

### Web framework

- Web endpoints should be in charge of receiving parameters, parsing/transforming them, use them to execute the needed calculation functions, and chain their input/output as needed.
- Adding comments to the execution chain is encouraged.
- If any function can raise an Exception, the whole execution chain must be contained in a `try/except` block.
- Each Route must ultimately return a `Response` instance, with proper response headers. For Flask, the `jsonify` function lets the user do this easily.
- Appropiate HTTP response codes are encouraged. If the execution is successful, a normal code 200 is implied in the jsonify function, but otherwise the proper 400/500 code should be set on the `Response` instance.
- Use the appropiate debug level when handling errors to return information about the problem, or just saying "Internal Server Error".

### Suggested procedure

The procedure to organize the code in a new module should follow these steps:

- DESIGN the functionality you want to implement. Think, group, and organize similar functionality.
- WRITE TESTS before coding, based on the design guidelines you reached. This way you can define what to expect and what not to do. You're still on time to change your design as you go.
- WRITE CODE to accomplish what you designed. Be a kind programmer and do not write code to specifically pass the tests. Always think in a general way; if one day your code is made into a module of its own, the refactor will be a breeze.
