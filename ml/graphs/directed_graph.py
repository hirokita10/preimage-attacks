# -*- coding: utf-8 -*-
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


class DirectedGraph(object):

  def __init__(self, undirected_graph_yaml, verbose=True):
    self.verbose = verbose
    undirected_graph = nx.read_yaml(undirected_graph_yaml)
    self.graph = self.addDirections(undirected_graph)


  def saveGraph(self, filename):
    if self.verbose:
      print('Saving directed Bayesian network as "%s"...' % filename)
    nx.write_yaml(self.graph, filename)


  def visualizeGraph(self):
    if self.verbose:
      print('Showing directed Bayesian network...')
    nx.draw_spectral(self.graph, with_labels=True)
    plt.show()


  def addDirections(self, undirected_graph):
    if self.verbose:
      print('Adding directions to undirected Bayesian network...')

    num_hash_input_bits = undirected_graph.number_of_nodes() - 256
    hash_input_bits = set(range(256, 256 + num_hash_input_bits))
    for hash_input_bit in hash_input_bits:
      neighbors = set(undirected_graph[hash_input_bit].keys())
      shared = neighbors.intersection(hash_input_bits)
      assert len(shared) == 0, 'No hash input bits should be connected!'

    g = nx.DiGraph()
    queue = list(hash_input_bits)
    visited = set()
    # Breadth-first search, starting from all hash input bits. Since none
    # of them are connected, no arrows will point TOWARDS a hash input bit,
    # which is what we want. The hash input bits are random and should not
    # be conditionally dependent on anything.
    while len(queue) > 0:
      node = queue.pop(0)
      visited.add(node)
      neighbors = list(undirected_graph[node].keys())

      for neighbor in neighbors:
        if (not g.has_edge(node, neighbor)) and \
           (not g.has_edge(neighbor, node)):
           g.add_edge(node, neighbor)

        if neighbor in visited: continue;
        queue.append(neighbor)

    if self.verbose:
      print('The directed BN has %d edges.' % g.number_of_edges())

    assert len(list(nx.simple_cycles(g))) == 0, 'BN should have no cycles'
    return g
