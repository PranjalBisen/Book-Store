// ============================================================
// trie_wrapper.cpp
//
// This single file contains:
//   1) The Trie data structure (your C++ code from c.cpp)
//   2) The pybind11 bindings that expose it to Python
//
// HOW IT WORKS:
//   pybind11 is a header-only C++ library. When we compile this
//   file, the compiler produces a .so (shared object) file that
//   Python can directly "import" like a normal Python module.
//
//   The PYBIND11_MODULE macro at the bottom tells pybind11:
//     "Create a Python module called 'trie_module' and expose
//      these C++ classes and methods as Python objects."
//
//   pybind11/stl.h automatically converts:
//     C++ vector<string>  <-->  Python list[str]
//     C++ string          <-->  Python str
//     C++ bool            <-->  Python bool
//
// COMPILE WITH:
//   c++ -O3 -shared -std=c++17 -fPIC \
//     $(python -m pybind11 --includes) \
//     trie_wrapper.cpp \
//     -o trie_module$(python -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))") \
//     -undefined dynamic_lookup
// ============================================================

#include <vector>
#include <string>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

using namespace std;
namespace py=pybind11;

// ---- Trie with full ASCII support (128 chars, not just a-z) ----

const int CHARSET=128;

struct Node{
  Node *links[CHARSET];
  bool flag1,flag2;
  Node(){
    for(int i=0;i<CHARSET;i++)links[i]=NULL;
    flag1=false;
    flag2=false;
  }
  bool containsKey(char c){return (links[(int)c]!=NULL);}
  void put(char c,Node *node){links[(int)c]=node;}
  Node *get(char c){return links[(int)c];}
  void setEnd(){flag1=true;flag2=false;}
  bool check(){return flag1;}
  void setEnd2(){flag2=true;}
  bool checkEnd2(){return flag2;}
};

class Trie{
public:
  Node *root;

  Trie(){root=new Node();}

  void insert(string s){
    Node *node=root;
    for(auto &it:s){
      if(!node->containsKey(it)){
        node->put(it,new Node());
      }
      node=node->get(it);
    }
    node->setEnd();
  }

  bool search(string s){
    Node *node=root;
    for(auto &it:s){
      if(!node->containsKey(it)){
        return false;
      }
      node=node->get(it);
    }
    return node->check()&&(!node->checkEnd2());
  }

  void remove(string s){
    Node *node=root;
    for(auto &it:s){
      if(!node->containsKey(it)){
        return;
      }
      node=node->get(it);
    }
    node->setEnd2();
  }

  void dfs(Node *node,string &s,vector<string> &v){
    if(!node->checkEnd2()&&node->check()){
      v.push_back(s);
    }
    for(int i=0;i<CHARSET;i++){
      if(node->links[i]!=NULL){
        char it=(char)i;
        s.push_back(it);
        dfs(node->links[i],s,v);
        s.pop_back();
      }
    }
  }

  vector<string> find(string s){
    Node *node=root;
    for(auto &it:s){
      if(!node->containsKey(it)){
        return {};
      }
      node=node->get(it);
    }
    vector<string>v;
    string ss=s;
    dfs(node,ss,v);
    return v;
  }
};

// ---- pybind11 bindings ----
// This macro creates a Python module named "trie_module"
// Inside it, we expose the Trie class with 4 methods

PYBIND11_MODULE(trie_module,m){
    m.doc()="C++ Trie exposed to Python via pybind11";

    py::class_<Trie>(m,"Trie")
        .def(py::init<>())                          // Trie()  -> constructor
        .def("insert",&Trie::insert)                // t.insert("word")
        .def("search",&Trie::search)                // t.search("word") -> bool
        .def("remove",&Trie::remove)                // t.remove("word")
        .def("autocomplete",&Trie::find);           // t.autocomplete("prefix") -> list[str]
}
