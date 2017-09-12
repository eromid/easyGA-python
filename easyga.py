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

import random
from itertools import combinations
from multiprocessing import Pool


class Chromasome:
  """
  The genetic material of an individual.

  """

  def __init__(self, n_bits, fitness_fnc):
    """
    Constructor for Chromasome objects.
    Args:
      n_bits (int): The length of the bitstring needed to encode an individual's characteristics.
      fitness_fnc (Callable): A callable (function or lambda) that takes the bitstring as a 
      parameter and returns its fitness score.

    """
    self.n_bits = n_bits
    self.fitness_fnc = fitness_fnc
    self.fitness_val = None
    self.bit_string = [0 for i in range(n_bits)]
    self.fitness_calculated = False

  def randomise(self):
    """
    Randomise the bits in the bitstring. Useful for initialising in the first generation.
    Returns:
      :obj:`Chromasome`: Refernce to self for method chaining.

    """
    self.bit_string = [random.choice([0, 1]) for i in range(self.n_bits)]
    return self

  def mutate(self, rate=0.001):
    """
    Mutate the individual - randomly flip some of the bits in the bitstring.
    Args:
      rate (float): The probability each individual bit will be flipped.

    Returns:
      :obj:`Chromasome`: Refernce to self for method chaining.

    """
    for i in range(len(self.bit_string)):
      if random.random() <= rate:
        self.bit_string[i] = int(not self.bit_string[i])
    return self

  def fitness(self):
    """
    Get the fitness for this individual. Checks for cached fitness score before calling the (potentially 
    expensive) fitness function

    Returns:
      :obj:`Chromasome`: Refernce to self for method chaining.

    """
    if self.fitness_val is not None:  # check for a cached solution to the fitness function...
      return self.fitness_val
    else:  # otherwise evaluate it.
      self.fitness_val = self.fitness_fnc(self.bit_string)
      return self.fitness_val

  def crossoverSinglePoint(self, mate, pivot):
    """
    Combine this individual with another to create an offspring individual with 
    some traits from each parent.
    Args:
      mate (:obj:`Chromasome`):  The individual we are combining with this one.
      pivot (int): index to split the bitstrings at. The child bitstring is equal to this
              individual's left `pivot`, and the `mate` individual right of `pivot`.

    """
    child = Chromasome(self.n_bits, self.fitness_fnc)
    child.bit_string = self.bit_string[:pivot] + mate.bit_string[pivot:]
    return child

  def crossoverUniform(self, mate):
    """
    Combine this individual with another to create an offspring individual with 
    some traits from each parent. Takes each bit randomly from a parent with equal probability
    Args:
      mate (:obj:`Chromasome`): The individual we are combining with this one.

    Returns:
      :obj:`Chromasome`: The new child individual.

    """
    parents = [self, mate]
    child = Chromasome(self.n_bits, self.fitness_fnc)
    for i in xrange(len(self.bit_string)):
      choice = int(random.random() > 0.5)
      child.bit_string[i] = parents[choice].bit_string[i]
    return child

  def asHex(self):
    """
    The hexadecimal representation of this individual.
    Returns:
      str: The hex representation.
    
    """
    exponent = 0
    total = 0

    for i in reversed(self.bit_string):
      total += i * (2 ** exponent)
      exponent += 1

    return hex(total)

  def __str__(self):
    """
    Binary representation of the bit string

    """
    return str(self.bit_string)


class GeneticAlgorithm:
  """
  A abstract general genetic algorithm. Your implementation should use this as its base class
  and override the following methods:
  `selection`: Defines how the "parents" are selected.
  `crossover`: Defines how the "parents" are combined to produce the next generation.
  `mutate`:    Defines how the offspring are mutated to allow drift in the population.

  There are built in options for some of the above:
    `getBestPairs`, `getRoulettePairs` for `selection` method.
    `singlePointCrossover`, `uniformCrossover` for `crossover` method.

  """

  def __init__(self, population_size, bit_string_len, fitness_fnc):
    """
    Create a population and find the fitness of the first generation.
    
    Args:
      population_size (int): The number of individuals to maintain in the population.
      bit_string_len (int): The length of the bit string of each individual.
      fitness_fnc (Callable): Function to call on the individual to determine its fitness.

    """
    self.population_size = population_size
    self.fitness_fnc = fitness_fnc
    self.bit_string_len = bit_string_len
    self.population = [Chromasome(self.bit_string_len, self.fitness_fnc).randomise() for i in range(population_size)]
    # self.elite_cutoff = 16 #TODO: remove?
    self.updateAllFitness()

  def selection(self):
    """
    Must be overloaded in a subclass to determine how to perform selection.
    
    Returns:
     list of tuple of :obj:`Chromasome`: The pairs to be recombined into the next generation.
    
    """
    raise NotImplementedError("`Selection` method must be overloaded in a subclass")

  def crossover(self, parent_pairs):
    """
    Must be overloaded in a subclass to determine how to perform crossover.
    
    Args:
      parent_pairs (tuple of :obj:`Chromasome`): Parent pairs to be recombined

    Returns:
      list of :obj:`Chromasome`: The new generation of individuals

    """
    raise NotImplementedError("`Crossover` method must be overloaded in a subclass")

  def mutate(self):
    """
    Must be overloaded in a subclass to determine how to perform crossover.
    
    """
    raise NotImplementedError("`Mutate` method must be overloaded in a subclass")

  def nextGeneration(self):
    """
    Perform the steps necessary to advance the population:
      1. Calculate all fitnesses
      2. Select parent pairs
      3. Recombine individuals
      4. Mutate the new generation
      
    """
    self.updateAllFitness()
    parent_pairs = self.selection()
    self.population = self.crossover(parent_pairs)
    self.mutate()

  def updateAllFitness(self, n_workers=16):
    """
    Recompute the fitness of all of the individuals. Uses a work pool to parallelize the fitness calculation.

    Args:
      n_workers (int): The number of workers in the work pool.

    """
    work_pool = Pool(n_workers)
    updated_fitness = work_pool.map(self.fitness_fnc, [chromasome.bit_string for chromasome in self.population])

    for i in xrange(len(self.population)):
      self.population[i].fitness_val = updated_fitness[i]
    work_pool.close()

  def getBestPairs(self, n_pairs, n_elites):
    """
    A built in selection method to call in `selection`. Gets random pairs from the best individuals
    in the population. We sort the population and choose random unique pairings from the top n_elites.
    with uniform probability.
  
    Args:
      n_pairs (int): The number of pairs to generate.
      n_elites (int): Only the best n_elites are considered for inclusion in the pairings.

    """
    self.population = sorted(self.population, key=lambda genotype: genotype.fitness(), reverse=True)
    elites = self.population[:n_pairs]
    parent_pairs = []
    while len(parent_pairs) < self.population_size:
      p1 = random.choice(elites)
      p2 = random.choice(elites)
      if p1 is not p2 and (p1, p2) not in parent_pairs:
        parent_pairs.append((p1, p2))
    return parent_pairs

  def getRoulettePairs(self, n_pairs):
    """
    A built in selection method to call in `selection`. Gets random pairs from the best pairs from
    the population. We sort the population and choose random unique pairings from the top 50% with
    uniform probability.
    Args:
      n_pairs (int): The number of pairs required to form the next generation. This typically
      depends on the crossover method being used.

    Returns:
      list of tuple of :obj:`Chromasomes`: The parent pairs for the next generation.

    """
    parent_pairs = []
    self.population = sorted(self.population, key=lambda genotype: genotype.fitness(), reverse=True)
    total_fitness = sum(individual.fitness() for individual in self.population)
    while len(parent_pairs) < n_pairs:
      r = random.uniform(0.0, total_fitness)
      cumulative_fitness = 0.0
      left_parent = None
      for individual in self.population:
        cumulative_fitness += individual.fitness()
        if cumulative_fitness >= r:
          left_parent = individual
          break
      if left_parent is None:
        pass
      # Choose a right parent.
      r = random.uniform(0.0, total_fitness)
      cumulative_fitness = 0.0
      right_parent = None
      for individual in self.population:
        cumulative_fitness += individual.fitness()
        if cumulative_fitness >= r:
          right_parent = individual
          break
      if right_parent is None:
        pass

      # Add the parent tuple if they are not the same and not already present.
      if left_parent is not right_parent and (left_parent, right_parent) not in parent_pairs:
        parent_pairs.append((left_parent, right_parent))
    return parent_pairs

  def uniformCrossover(self, parent_pairs):
    """
    Built in method for recombining parent individuals. Each bit has an equal chance to be inherited
    from each parent.
    Args:
      parent_pairs (list of tuple of :obj:`Chromasome`): The pairs of parents. The length of this
      should be equal to the population size.
    Returns:
      list of :obj:`Chromasome`: The new generation.

    """
    if len(parent_pairs) != self.population_size:
      raise ValueError("Uniform crossover expects {} parent pairs; given {}." \
        .format(self.population_size, len(parent_pairs)))
    new_generation = [p1.crossoverUniform(p2) for p1, p2 in parent_pairs]
    return new_generation

  def singlePointCrossover(self, parent_pairs, pivot=None):
    """
    Built in method for producing a new generation. The bit strings of the parents are split at the
    `pivot` and the "halves" swapped between the parents, producing two offspring for each parent
    pair.
    Args:
      parent_pairs (list of tuple of :obj:`Chromasome`): The pairs of parents.
      pivot (int): The index at which to "chop" the bit strings.
    Returns:
      list of :obj:`Chromasome`: The new generation.
    """
    if len(parent_pairs) != self.population_size / 2:
      raise ValueError("Single point crossover expects {} parent pairs; given {}." \
        .format(self.population_size / 2, len(parent_pairs)))
    if pivot is None:
      pivot = self.bit_string_len / 2
    new_generation = [p1.crossoverSinglePoint(p2, pivot) for p1, p2 in parent_pairs]
    new_generation += [p2.crossoverSinglePoint(p1, pivot) for p1, p2 in parent_pairs]
    return new_generation

  def mutateAll(self, rate):
    """
    Mutate all the individuals in the population.
    Args:
      rate (int): The probability that each individual bit will be flipped.
                  Must be [0..1].

    """
    if (rate < 0.0) or (rate > 1.0):
      raise ValueError("Mutation rate must be between 0 and 1.")
    for individual in self.population:
      individual.mutate(rate)


  def avgFitness(self):
    """
    Get the mean fitness of the current population.
    Returns:
      float: The mean fitness of the population.

    """
    return sum([genotype.fitness() for genotype in self.population]) / float(self.population_size)

  def maxFitness(self):
    """
    Get the fitness of the fittest individual in the current population.
    Returns:
      float: The fitness of the fittest individual in the population.

    """
    return max([chromasome.fitness() for chromasome in self.population])

  def minFitness(self):
    """
    Get the fitness of the least fit individual in the current population.
    Returns:
      float: The fitness of the least fit individual in the population.

    """
    return min([chromasome.fitness() for chromasome in self.population])

  def __str__(self):
    """
    String representation of the population; the hex string of each individual
    no new lines.
    Returns:
      str: String representation of the population.
    """
    return "\n".join([i.asHex() for i in self.population])


  def getBestIndividual(self):
    """
    Get the fittest individual in the current population.
    Returns:
      :obj:`Chromasome`: The fittest individual in the population.

    """
    return max(self.population, key=lambda chromasome: chromasome.fitness())
