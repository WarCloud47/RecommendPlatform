import numpy as np
import math
#from sklearn.metrics import mean_squared_error, mean_absolute_error
import pickle


def dump(file_name, model):
    dump_obj =  model
    pickle.dump(dump_obj, open(file_name, 'wb'),  protocol=pickle.HIGHEST_PROTOCOL)
        
def load(file_name):
    dump_obj = pickle.load(open(file_name, 'rb'))
    return dump_obj

class MF():

    def __init__(self, ratings, num_factors = 100, alpha = .005, lambda_reg = .02, num_epochs = 10):

        self.ratings = ratings
        self.num_users, self.num_items = ratings.shape
        self.num_factors = num_factors
        self.alpha = alpha
        self.lambda_reg = lambda_reg
        self.num_epochs = num_epochs
    
    def fit(self):
        # инициализация факторных матриц
        self.P = np.random.normal(scale=1./self.num_factors, size=(self.num_users, self.num_factors))
        self.Q = np.random.normal(scale=1./self.num_factors, size=(self.num_items, self.num_factors))

        # инициализация базовых предикторов
        self.b_u = np.zeros(self.num_users)
        self.b_i = np.zeros(self.num_items)
        self.b_mean = np.mean(self.ratings[np.where(self.ratings != 0)])

        # Создание списка обучающих данных
        self.samples = [
            (u, i, self.ratings[u, i])
            for u in range(self.num_users)
            for i in range(self.num_items)
            if self.ratings[u, i] > 0
        ]

        # Выполнение алгоритма обучения по количеству эпох
        training_process = []
        for i in range(self.num_epochs):
            np.random.shuffle(self.samples)
            self.sgd()
            mae = self.mae()
            rmse = self.rmse()
            training_process.append((i, mae, rmse))
            if (i+1) % 5 == 0:
                print("Эпоха: %d; error_mae = %.4f; error_rmse = %.4f" % (i+1, mae, rmse))

        return training_process

    def sgd(self):
        """
        Метод стохастического градиентного спуска
        """
        for u, i, r_ui in self.samples:
            # Вычисление ошибки и прогноза
            e_ui = (r_ui - self.predict(u, i))

            # Обновление базовые предикторы
            self.b_u[u] += self.alpha * (e_ui - self.lambda_reg * self.b_u[u])
            self.b_i[i] += self.alpha * (e_ui - self.lambda_reg * self.b_i[i])

            # Обновление факторов пользователей и предметов
            P_u = self.P[u, :][:] 
            Q_i = self.Q[i, :][:]

            self.P[u, :] += self.alpha * (e_ui * Q_i - self.lambda_reg * P_u)

            self.Q[i, :] += self.alpha * (e_ui * P_u - self.lambda_reg * Q_i) 
   
    def predict(self, u, i):
        """
        Получение прогноз рейтинга пользователя u предмету i
        """
        prediction = self.b_mean + self.b_u[u] + self.b_i[i] + np.dot(self.P[u, :], self.Q[i, :].T)
        return prediction

    def full_matrix(self):
        """
        Расчет полной матрицы прогнозов
        """
        return self.b_mean + self.b_u[:,np.newaxis] + self.b_i[np.newaxis:,] + np.dot(self.P, self.Q.T)

    def rmse(self):
        """
        Функция расчета rmse
        """
        iz, jz = self.ratings.nonzero()
        predicted = self.full_matrix()
        error = 0
        for i, j in zip(iz, jz):
            error += pow(self.ratings[i, j] - predicted[i, j], 2)
        return np.sqrt(error / self.num_items)

    def mae(self):
        """
        Функция расчета mae
        """
        iz, jz = self.ratings.nonzero()
        predicted = self.full_matrix()
        error = 0
        for i, j in zip(iz, jz):
            error += math.fabs(self.ratings[i, j] - predicted[i, j])
        return error / self.num_items
