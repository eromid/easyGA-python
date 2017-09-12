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

import unittest
import easyga as ega

# Unit tests using the unittest module (http://docs.python.org/2/library/unittest.html)

def fitness(bit_string):
  """
  Toy fitness function, returns 2^x, where x is the number of 'one' bits in
  the bit string.
  
  """
  return 2**sum(bit_string)


# Tests for the chromasome class:

class ChromasomeTests(unittest.TestCase):

  def setUp(self):  
    self.chromasome = ega.Chromasome(32, fitness)


  def checkBitString(self):
    # Check bit string length
    self.assertEqual(len(self.chromasome.bit_string), 32)
    # Check we only have 1s and/or 0s
    self.assertTrue(set(self.chromasome.bit_string).issubset(set([0,1])))


  def test_bitStringInit(self):
    # Check length and contents of initial bitstring. Should be 32 * 0s
    self.assertEqual(self.chromasome.bit_string, [0 for i in xrange(32)])


  def test_randomise(self):
    # Check randomise maintains bit string integrity.
    self.chromasome.randomise()
    self.checkBitString()


  def test_mutate(self):
    # Check mutate maintains bit string integrity.
    self.chromasome.mutate()
    self.checkBitString()


  def test_fitness(self):
    # Check fitness value is that of the function we gave it and
    # that it leaves the bit_string intact.
    self.chromasome.randomise()
    self.chromasome.mutate()
    result = self.chromasome.fitness()
    self.assertEqual(result, fitness(self.chromasome.bit_string))
    self.checkBitString()


  def test_SinglePointCross(self):
    # Test single point crossover works as expected
    other = ega.Chromasome(32, fitness)
    other.randomise()
    child = self.chromasome.crossoverSinglePoint(other, 16)
    self.assertIsInstance(child, ega.Chromasome)
    self.assertEqual(self.chromasome.bit_string[:16], child.bit_string[:16])
    self.assertEqual(          other.bit_string[16:], child.bit_string[16:])
    
    self.chromasome = child
    self.checkBitString()
    
  def test_uniformCrossover(self):
    # Test uniform crossover works as expected
    other = ega.Chromasome(32, fitness)
    other.randomise()
    child = self.chromasome.crossoverUniform(other)
    self.assertIsInstance(child, ega.Chromasome)
    for i in xrange(len(child.bit_string)):
      child_bit    = child.bit_string[i]
      parent_a_bit = self.chromasome.bit_string[i]
      parent_b_bit = other.bit_string[i]
      self.assertTrue( (child_bit == parent_a_bit) or (child_bit == parent_b_bit) )

    self.chromasome = child
    self.checkBitString()
  
  
  def test_strMagicMethod(self):
    # Test the str magic method returns a string
    self.assertIsInstance(self.chromasome.__str__(), str)
    

# Implementation of a ega for test purposes.  
class Testega(ega.GeneticAlgorithm):

  def selection(self):
    """
    Takes no arguments, returns the list of parent tuples to recombine into the next generation.
    
    """
    return self.getRoulettePairs(len(self.population))


  def crossover(self, parent_pairs):
    """   
    Takes argument of parent pairs to be recombined. Non returning, but
    updates the population attribute to become the next generation.
    
    """
    return self.uniformCrossover(parent_pairs)


  def mutate(self):
    """
    Must be overloaded in a subclass to determine how to perform crossover.
    
    """
    self.mutateAll(0.01)


# Tests for the GeneticAlgorithm class:

class egaTests(unittest.TestCase):
  
  def setUp(self):
    """
    Run at the start of the testing proceedure.
    
    """
    self.ga = Testega(32, 32, fitness)
    
  def test_Init(self):
    """
    Test the constructor.
    
    """
    self.assertEqual(len(self.ga.population), 32)
    for c in self.ga.population:
      self.assertIsInstance(c, ega.Chromasome)
      
  
  def test_selection(self):
    """
    Test the selection routine.
    
    """
    parent_pairs = self.ga.selection()
    
    for pair in parent_pairs:
      self.assertIsInstance(pair[0], ega.Chromasome)
      self.assertIsInstance(pair[1], ega.Chromasome)
      self.assertEqual(len(pair), 2)


  def test_crossover(self):
    """
    Test the crossover routine.
    
    """
    parent_pairs = self.ga.selection()
    self.ga.population = self.ga.crossover(parent_pairs)
    
    self.assertEqual(len(self.ga.population), 32)
    for c in self.ga.population:
      self.assertIsInstance(c, ega.Chromasome)


  def test_mutation(self):
    """
    Test mutation routine.
    
    """
    parent_pairs = self.ga.selection()
    self.ga.population = self.ga.crossover(parent_pairs)
    self.ga.mutate()
    
    self.assertEqual(len(self.ga.population), 32)
    for c in self.ga.population:
      self.assertIsInstance(c, ega.Chromasome)

  def test_nextGeneration(self):
    """
    Test forming the next generation.
    
    """
    self.ga.nextGeneration()
    
    self.assertEqual(len(self.ga.population), 32)
    for c in self.ga.population:
      self.assertIsInstance(c, ega.Chromasome)


if __name__ ==  "__main__":
  unittest.main()
