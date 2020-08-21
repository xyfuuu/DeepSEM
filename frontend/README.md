# Front-end

The PC port's front end design with Qt.



Quick file introduction:

- ` images/` : sources fold
- `mainwindow.cpp` : main part for the input canvas
- `diagramscene` & `diagramitem` & `diagramtextitem` & `arrow`: components of the canvas
- `outputwindow`:  parse the output model and display it as picture



Notice：

1. Relationship between the two windows haven't been established yet, so please change the `w.show()` annotation in `main.cpp` to alter which window to show during the debug process.  
2. The input canvas design is modified from Qt Official Example "diagramscene", check it out if there's some difficult understanding the code.