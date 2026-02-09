from pathlib import Path

from codereport import CodeReport, ReportItem

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


def test_create(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "myclass.h").write_text(file_a.strip())
    (src / "myclass.cxx").write_text(file_b.strip())
    (src / "main.cxx").write_text(file_c.strip())

    items = [
        ReportItem(str(src / "myclass.cxx"), 4, "info", "This is a great class", "awesomeness"),
        ReportItem(str(src / "main.cxx"), 2, "warning", "This is not a great function", "executable"),
    ]

    report_dir = tmp_path / "report"

    cp = CodeReport(items)
    cp.render(report_dir)

    assert report_dir.exists(), "Report directory created"
    report_files = [f.name for f in report_dir.iterdir()]
    assert "index.html" in report_files, "Index page is created"

