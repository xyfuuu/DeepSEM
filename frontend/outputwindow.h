#ifndef OUTPUTWINDOW_H
#define OUTPUTWINDOW_H

#include <QDialog>

namespace Ui {
class OutputWindow;
}

class OutputWindow : public QDialog
{
    Q_OBJECT

public:
    explicit OutputWindow(QWidget *parent = nullptr);
    ~OutputWindow();
    void visualization();

private:
    Ui::OutputWindow *ui;
};

#endif
