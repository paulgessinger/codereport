from codereport import CodeReport, ReportItem

from fs.memoryfs import MemoryFS
from fs.osfs import OSFS

file_a = """
#pragma once

class MyClass {

    MyClass(); // awesome constructor

};
"""

file_b = """
// this is the implementation file
#include "myclass.h"

MyClass::MyClass() {

}
"""

file_c = """
#include <iostream>
void main() {
    std::cout << "hallo welt" << std::endl;
}

"""


def test_create():
    fs = MemoryFS()
    # fs = OSFS("/tmp/cprtest")
    fs.makedir("src", recreate=True)
    fs.settext("src/myclass.h", file_a.strip())
    fs.settext("src/myclass.cxx", file_b.strip())
    fs.settext("src/main.cxx", file_c.strip())
    fs.tree()

    items = [ReportItem("src/myclass.cxx", 4, "info", "This is a great class", "awesomeness"),
             ReportItem("src/main.cxx", 2, "warning", "This is not a great function", "executable")]

    cp = CodeReport(items, srcfs=fs, destfs=fs)
    cp.render("report")

    assert fs.exists("report"), "Report directory created"
    report_files = fs.listdir("report")
    assert "src_myclass.cxx.html" in report_files, "Slashes are converted to underscores"
    assert "src_main.cxx.html" in report_files, "Slashes are converted to underscores"

    assert "index.html" in report_files, "Index page is created"
    print(report_files)


