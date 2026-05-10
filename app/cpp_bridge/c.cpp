#include <iostream>
#include <vector>
#include <string>
#include <cstring>

using namespace std;

struct Node {
  Node *links[26];
  bool flag1, flag2;
  Node() {
    for (int i = 0; i < 26; i++)
      links[i] = NULL;
    flag1 = false;
    flag2 = false;
  }
  bool containsKey(char c) { return (links[c - 'a'] != NULL); }
  void put(char c, Node *node) { links[c - 'a'] = node; }
  Node *get(char c) { return links[c - 'a']; }
  void setEnd() {
    flag1 = true;
    flag2 = false;
  }
  bool check() { return flag1; }
  void setEnd2() { flag2 = true; }
  bool checkEnd2() { return flag2; }
};

class Trie {
public:
  Node *root;

  Trie() { root = new Node(); }
  void insert(string s) {
    Node *node = root;
    for (auto &it : s) {
      if (!node->containsKey(it)) {
        node->put(it, new Node());
      }
      node = node->get(it);
    }
    node->setEnd();
  }
  bool search(string s) {
    Node *node = root;
    for (auto &it : s) {
      if (!node->containsKey(it)) {
        return false;
      }
      node = node->get(it);
    }
    return node->check() && (!node->checkEnd2());
  }
  void remove(string s) {
    Node *node = root;
    for (auto &it : s) {
      if (!node->containsKey(it)) {
        return;
      }
      node = node->get(it);
    }
    node->setEnd2();
  }
  void dfs(Node *node, string &s, vector<string> &v) {
    if (!node->checkEnd2() && node->check()) {
      v.push_back(s);
    }
    for (int i = 0; i < 26; i++) {
      if (node->links[i] != NULL) {
        auto it = i + 'a';
        s.push_back(it);
        dfs(node->links[i], s, v);
        s.pop_back();
      }
    }
  }
  vector<string> find(string s) {
    Node *node = root;
    for (auto &it : s) {
      if (!node->containsKey(it)) {
        return {};
      }
      node = node->get(it);
    }
    vector<string> v;
    string ss = s;
    dfs(node, ss, v);
    return v;
  }
};

int main() {
  Trie t;
  cin.tie(0)->sync_with_stdio(0);
  return 0;
}