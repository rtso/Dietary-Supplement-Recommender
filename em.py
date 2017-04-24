import numpy as np
from sklearn.cluster import KMeans

np.seterr(all='raise')
"""
cluster_em: cluster data using EM algorithm and GMM model,
            optionally as a batch process
inputs:
        X -- N x D matrix where N = number of data points and D = dimensions
        K -- number of cluster centers
        batch size -- number of data points to examine per step
                     (uses all data points if batch not specified)
        tolerance -- stopping condition for optimization
        max_iter -- maximum number of iterations
        verbose -- print Q value at each iteration

outputs:
        dictionary with the following fields:
        'mu' -- K x D matrix of cluster centers
        'pi' -- mixing weights for GMM
        'iterations' -- number of iterations executed
"""


def cluster_em(X, k, mode, batch_size=None, tolerance=1, max_iter=25, verbose=False):

    # Make model
    if mode == 'Gaussian':
        model = GaussianMixtureModel(X, k)
    elif mode == 'Topic':
        model = TopicModel(X, k)

    # get a random batch of size batch_size
    if batch_size:
        batch = np.random.choice(model.N, batch_size)
    else:
        batch = range(model.N)

    # iterate until diff within tolerance or max iterations exceeded
    diff = np.inf
    q_old = model.e_step(batch)
    cur_iter = 0
    while diff > tolerance:

        # get a random batch of size batch_size
        if batch_size:
            batch = np.random.choice(model.N, batch_size)
        else:
            batch = range(model.N)

        if verbose:
            print('q =', q_old)
        if cur_iter > max_iter:
            print('Max iterations exceeded')
            break

        # update mixture model parameters
        model.m_step(batch)
        q_new = model.e_step(batch)
        diff = abs(q_new - q_old)
        q_old = q_new
        cur_iter += 1

    if verbose:
        print('q final =', q_old)

    if mode == 'Gaussian':
        return {'mu': model.mu, 'pi': model.pi, 'iterations': cur_iter}
    elif mode == 'Topic':
        return {'p': model.p, 'pi': model.pi, 'iterations': cur_iter}


"""
GaussianMixtureModel class
contains the parameters of the GMM model:

K -- number of cluster centers
N -- number of data points
D -- dimensions of data
mu -- K x D matrix of cluster centers
pi -- length K vector of mixing weights
w -- probability distribution over hidden variables

member functions:
e_step -- evaluate Q function on given batch of indicies
m_step -- maximize Q function on given batch of indicies
"""


class GaussianMixtureModel:

    """
    constructor takes 2 args:
    X -- N x D data matrix
    K -- number of cluster centers
    """

    def __init__(self, x, k):
        self.X = x
        self.N = x.shape[0]
        self.D = x.shape[1]
        self.K = k
        self.mu = np.random.rand(k, self.D)
        self.pi = np.ones(k) / k
        self.w = np.random.rand(self.N, k)

    def e_step(self, batch):

        # evaluate Q function
        q = 0
        for i in batch:
            for j in range(self.K):
                q += (-.5 * sum(np.square(self.X[i, :] - self.mu[j, :])) + np.log(self.pi[j])) * self.w[i, j]
        return q

    def m_step(self, batch):

        # update distribution over hidden variables
        for i in batch:
            w_denominator = \
                sum([np.exp(-.5 * sum(np.square(self.X[i, :] - self.mu[k, :]))) * self.pi[k] for k in range(self.K)])
            for j in range(self.K):
                w_numerator = np.exp(-.5 * sum(np.square(self.X[i, :] - self.mu[j, :]))) * self.pi[j]
                self.w[i, j] = w_numerator / w_denominator
        tmp = np.zeros((self.N, self.D))

        # update means and mixing weights
        for j in range(self.K):
            for i in batch:
                tmp[i, :] = self.X[i, :] * self.w[i, j]
            mu_numerator = np.sum(tmp, 0)
            mu_denominator = sum([self.w[i, j] for i in batch])
            self.mu[j, :] = mu_numerator / mu_denominator
            self.pi[j] = mu_denominator / len(batch)


"""
TopicModel class

K -- number of topics
N -- number of documents
V -- size of vocabulary
mu -- K x V matrix of topic vocabulary distributions
pi -- length of K vector of mixing weights
w -- probability distribution over hidden variables

member functions:
e_step -- evaluate Q function on given batch of indices
m_step -- maximize Q function on given batch of indices
"""


class TopicModel():
    """
    Constructor takes 2 args:
    X -- N x V sparse data matrix in CSR format
    K -- number of topics
    """
    def __init__(self, x, k):
        self.X = x
        self.N = x.shape[0]
        self.V = x.shape[1]
        self.K = k
        self.pi = np.ones(k) / k
        self.w = np.random.rand(self.N, k)

        kmeans = KMeans(n_clusters=self.K).fit(x)
        self.p = kmeans.cluster_centers_ / self.V

    def e_step(self, batch):
        # Evaluate Q function
        return np.sum(np.multiply(np.dot(self.X, np.log(self.p).T) + np.log(self.pi), self.w))

    def m_step(self, batch):
        # Update distribution over hidden variables
        for i in batch:
            original_w_numerators = np.sum(np.multiply(self.X[i, :], np.log(self.p)), axis=1) + np.log(self.pi)
            b = np.max(original_w_numerators)
            w_numerator_exponents = original_w_numerators - b
            w_numerators = list()
            for k in range(self.K):
                if abs(w_numerator_exponents[k]) > 100:
                    w_numerators.append(0)
                else:
                    w_numerators.append(np.exp(w_numerator_exponents[k]))
            w_denominator = np.sum(w_numerators)
            self.w[i, :] = w_numerators / w_denominator

        # Update parameters
        tmp = np.zeros((self.N, self.V))
        for j in range(self.K):
            for i in batch:
                tmp[i, :] = self.X[i, :] * self.w[i, j]
            p_numerator = np.sum(tmp, 0)
            p_denominator = np.sum(p_numerator)
            # Smooth word counts in the topics
            smoothing_constant = 0.001
            p_numerator += smoothing_constant
            p_denominator += self.V * smoothing_constant
            self.p[j, :] = p_numerator / p_denominator
            self.pi[j] = np.sum(self.w[:, j]) / len(batch)
