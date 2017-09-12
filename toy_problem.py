#!/usr/bin/env python
# encoding: utf-8

"""
EasyGA

Copyright © 2017 Eromid (Olly)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

from easyga import GeneticAlgorithm


def fitness(bit_string):
  """
  The fitness function for our toy problem.

  """
  return sum(bit_string)


class ToySolver(GeneticAlgorithm):
  """
  A Genetic algorithm for solving our toy problem.

  """

  def selection(self):
    """
    Overridden method to select parent pairs

    """
    return self.getRoulettePairs(self.population_size/2)

  def crossover(self, parent_pairs):
    """
    Overridden method to recombine individuals.

    """
    return self.singlePointCrossover(parent_pairs)

  def mutate(self):
    """
    Overridden method to mutate individuals a fixed amount.

    """
    return self.mutateAll(0.01)


if __name__ == "__main__":

  pop_size = 256  # Number of individuals in the population
  n_bits   = 32   # Length of the bitstring
  max_generations = 1000  # Number of generations to go through

  # Construct the genetic algorithm object.
  ga = ToySolver(pop_size, n_bits, fitness)

  print "Maximising the number of 1s in the bitstring."
  print "Population size:", pop_size
  print "Bit string length", n_bits

  for i in xrange(max_generations):
    print "Average fitness:", ga.avgFitness(), "Best Fitness:", ga.maxFitness()
    if ga.maxFitness() == n_bits:
      print "Found best possible configuration individual in", i, "generations."
      exit(0)
    else:
      ga.nextGeneration()

  print "Ran for {} generations, failed to find best possible individual.".format(max_generations)
