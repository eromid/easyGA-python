# EasyGA #

EasyGA is a simple but extensible genetic algorithm framework written in Python 2.x (conversion to 3.x would be trivial, I just haven't needed to), released under the terms of the MIT license.

## Usage ##

An example of usage is provided in [`toy_problem.py`](toy_problem.py) where it tries to maximise the number of set bits in a bit string (not an impressive problem to solve, but it serves as a reasonable demonstration).

As the user, you need to do a few things:

1. Implement a fitness function
2. Subclass `GeneticAlgorithm`
    1. Override `selection` method
    2. Override `crossover` method
    3. Override `mutate` method
3. Instantiate your class
4. Call the `nextGeneration` method, as many times as required.

### Implementing a Fitness Function ###

This should take a bit string (a list of `1`s and `0`s) which represents the [phenotype](https://en.wikipedia.org/wiki/Phenotype) of the individual and return a number representing the fitness (>= 0) of the individual. In our toy problem, it looks like this:
```python
def fitness(bit_string):
  return sum(bit_string)
```

### Subclassing `GeneticAlgorithm` ###

This is where we choose the details of how the 'parent' individuals will be chosen and how they will be recombined into the next generation, and how and to what extent they will be mutated. 

For our toy problem, we take advantage of some of the methods built in to EasyGA, but you could instead define your own here. It's important that the selection method you use generates the correct number of parent pairs for the crossover method.

```python
class ToySolver(GeneticAlgorithm):
  """
  A Genetic algorithm for solving our toy problem.

  """

  def selection(self):
    """
    Overridden method to select parent pairs.

    """
    return self.getRoulettePairs(self.population_size/2)

  def crossover(self, parent_pairs):
    """
    Overridden method to recombine individuals.

    """
    return self.singlePointCrossover(parent_pairs)

  def mutate(self):
    """
    Overridden method to mutate individuals a fixed amount (0.01 probability a bit is flipped).

    """
    return self.mutateAll(0.01)
```

### Instantiating your class ###

This is as simple as calling the constructor with suitable values for the parameters for the population size, the number of bits in the bit string, and the `fitness` function we defined earlier.

```python
  pop_size = 256  # Number of individuals in the population
  n_bits   = 32   # Length of the bitstring
  ga = ToySolver(pop_size, n_bits, fitness)
```

### Calling `nextGeneration` ###

Calling this will take the current population, evaluate its fitness based on the `fitness` function you defined, select parents using your `selection` routine, combine them with your `crossover` routine and `mutate` these offspring. You'll generally perform this in a loop:

```python
while ga.maxFitness() < desired_fitness:
  ga.nextGeneration()
```
