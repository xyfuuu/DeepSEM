#include "mainwindow.h"
#include "outputwindow.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

//    OutputWindow w;
//    w.show();

    MainWindow w;
    w.setGeometry(100, 100, 800, 500);
    w.show();

    return a.exec();
}
