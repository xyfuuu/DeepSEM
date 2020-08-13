#include "outputwindow.h"
#include "ui_outputwindow.h"

#include <iostream>

using namespace std;


/**
 * A simple version of displaying the output model as a picture.
 *
 * Example of an input graph:
 *      factor1 =~ y1 + y3 + y4 + y5
 *      factor2 =~ x1 + x2 + x3
 *      factor3 =~ y2 + y6 + y7 + y8
 *      factor1 ~ factor3
 *      factor2 ~~ factor3
 *
 */
void OutputWindow::visualization() {
    // Open output file and rewrite the graph in dot
    freopen("graph.dot","w",stdout);

    // Start graphing
    cout<<"digraph G{"<<endl;
    // title
    cout<<"label=\"";
    cout<<"DSEM";
    cout<<"\";"<<endl;
    // direction
    cout<<"rankdir=LR;"<<endl;
    // shape
    cout<<"y1 [shape=box];"<<endl;
    cout<<"y2 [shape=box];"<<endl;
    cout<<"y3 [shape=box];"<<endl;
    cout<<"y4 [shape=box];"<<endl;
    cout<<"y5 [shape=box];"<<endl;
    cout<<"y6 [shape=box];"<<endl;
    cout<<"y7 [shape=box];"<<endl;
    cout<<"y8 [shape=box];"<<endl;
    cout<<"x1 [shape=box];"<<endl;
    cout<<"x2 [shape=box];"<<endl;
    cout<<"x3 [shape=box];"<<endl;
    // relationship
    cout<<"y1->factor1;"<<endl;
    cout<<"y3->factor1;"<<endl;
    cout<<"y4->factor1;"<<endl;
    cout<<"y5->factor1;"<<endl;
    cout<<"x1->factor2;"<<endl;
    cout<<"x2->factor2;"<<endl;
    cout<<"x3->factor2;"<<endl;
    cout<<"y2->factor3;"<<endl;
    cout<<"y6->factor3;"<<endl;
    cout<<"y7->factor3;"<<endl;
    cout<<"y8->factor3;"<<endl;
    cout<<"factor1->factor3;"<<endl;
    cout<<"factor2->factor3 [dir=both];"<<endl;
    cout<<"}"<<endl;

    string s = "dot -Tpng graph.dot -o output.png";
    const char* cmd = s.data();
    system(cmd);
}

OutputWindow::OutputWindow(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::OutputWindow)
{
    ui->setupUi(this);
    visualization();
    QPixmap pixmap("output.png");
    ui->label->setPixmap(pixmap);
    ui->label->setScaledContents(true);
    ui->label->show();
}

OutputWindow::~OutputWindow()
{
    delete ui;
}
