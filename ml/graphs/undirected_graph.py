# -*- coding: utf-8 -*-
import networkx as nx
import matplotlib.pyplot as plt


class UndirectedGraph(object):

  def __init__(self, prob, size, max_connections, verbose=True):
    self.prob = prob
    self.verbose = verbose
    self.max_connections = max_connections
    self.N, self.n = size # (number of samples, number of variables)
    self.graph = self.pruneGraph(self.createFullyConnectedGraph())


  def saveGraph(self, filename):
    if self.verbose:
      print('Saving undirected Bayesian network as "%s"...' % filename)

    nx.write_yaml(self.graph, filename)


  def visualizeGraph(self):
    if self.verbose:
      print('Showing undirected Bayesian network...')

    nx.draw_spectral(self.graph, with_labels=True)
    plt.show()


  def createFullyConnectedGraph(self):
    if self.verbose:
      print('Calculating mutual information scores...')

    graph = nx.Graph()
    counter = 0
    max_count = self.n * (self.n - 1) / 2

    for i in range(self.n):
      # (i, j) score is symmetric to (j, i) score so we only need to
      # calculate an upper-triangular matrix with zeros on the diagonal
      for j in range(i + 1, self.n):

        if i >= 256 and j >= 256:
          # No edges between hash input bit random variables
          break

        # Make the weight negative since we technically want a MAXIMUM
        # spanning tree (i.e. the most-negative minimum spanning tree)
        weight = -self.prob.iHat([i, j])
        graph.add_edge(i, j, weight=weight)

        counter += 1
        if counter % 10000 == 0 and self.verbose:
          print('%.2f%% done.' % (100.0 * counter / max_count))

    return graph


  def pruneGraph(self, fc_graph):
    graph = fc_graph.copy()

    prune = True
    while prune:
      prune = False
      for rv in graph.nodes():
        num_neighbors = len(graph[rv])
        if num_neighbors <= self.max_connections:
          continue

        # Prune away least negative edge
        prune = True
        neighbors = [n for n in graph.edges(rv, data='weight')]
        neighbors = list(sorted(neighbors, key=lambda n: n[2]))
        to_remove = neighbors[-1] # last one is LEAST negative
        graph.remove_edge(to_remove[0], to_remove[1])

    if self.verbose:
      print('The optimized BN has %d edges.' % graph.number_of_edges())

    return graph
