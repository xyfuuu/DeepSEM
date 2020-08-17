/********************************************************************************
** Form generated from reading UI file 'outputwindow.ui'
**
** Created by: Qt User Interface Compiler version 5.15.0
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_OUTPUTWINDOW_H
#define UI_OUTPUTWINDOW_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QDialog>
#include <QtWidgets/QDialogButtonBox>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QLabel>

QT_BEGIN_NAMESPACE

class Ui_OutputWindow
{
public:
    QGridLayout *gridLayout;
    QLabel *label;
    QDialogButtonBox *buttonBox;

    void setupUi(QDialog *OutputWindow)
    {
        if (OutputWindow->objectName().isEmpty())
            OutputWindow->setObjectName(QString::fromUtf8("OutputWindow"));
        OutputWindow->resize(512, 305);
        gridLayout = new QGridLayout(OutputWindow);
        gridLayout->setObjectName(QString::fromUtf8("gridLayout"));
        label = new QLabel(OutputWindow);
        label->setObjectName(QString::fromUtf8("label"));
        QSizePolicy sizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(label->sizePolicy().hasHeightForWidth());
        label->setSizePolicy(sizePolicy);

        gridLayout->addWidget(label, 0, 0, 1, 1);

        buttonBox = new QDialogButtonBox(OutputWindow);
        buttonBox->setObjectName(QString::fromUtf8("buttonBox"));
        buttonBox->setOrientation(Qt::Horizontal);
        buttonBox->setStandardButtons(QDialogButtonBox::Cancel|QDialogButtonBox::Ok);

        gridLayout->addWidget(buttonBox, 1, 0, 1, 1);


        retranslateUi(OutputWindow);
        QObject::connect(buttonBox, SIGNAL(rejected()), OutputWindow, SLOT(reject()));
        QObject::connect(buttonBox, SIGNAL(accepted()), OutputWindow, SLOT(accept()));

        QMetaObject::connectSlotsByName(OutputWindow);
    } // setupUi

    void retranslateUi(QDialog *OutputWindow)
    {
        OutputWindow->setWindowTitle(QCoreApplication::translate("OutputWindow", "Dialog", nullptr));
        label->setText(QCoreApplication::translate("OutputWindow", "TextLabel", nullptr));
    } // retranslateUi

};

namespace Ui {
    class OutputWindow: public Ui_OutputWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_OUTPUTWINDOW_H
