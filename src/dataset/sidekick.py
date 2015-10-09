from __future__ import print_function
from .dataset import Dataset, DatasetError
from .project import Project
import numpy as np


class Sidekick(Dataset):
    def __init__(self):
        super(Sidekick, self).__init__(self.__class__.__name__)
        self.data_dir += "/sidekick"

    ###############
    # Access sample
    ###############

    def __getitem__(self, project_id):
        """
        Get a project in the Sidekick dataset.

        Allows:
        >>>> sk = Sidekick()
        >>>> project = sk['14035777']

        :param project_id:
        :return:
        """
        try:
            return self._load_project(project_id)
        except ProjectNotFound:
            if not self.data:
                self.load()
            for project in self.data:
                if project_id == project.project_id:
                    return project
            raise ProjectNotFound("Project %s not found")

    def __iter__(self):
        """
        Iterator over projects in Sidekick dataset.

        Allows:
        >>>> sk = Sidekick()
        >>>> for project in sk:
        >>>>    print project

        :return:
        """
        for project in self.data:
            yield project


    ###########
    # Load data
    ###########

    def load(self):
        """
        Load Sidekick data.
        """
        print('Loading projects...')
        projects = np.load('%s/projects.npy' % (self.data_dir, ))
        print('Loading statuses...')
        statuses = self._load_binary('%s/statuses.pkl' % (self.data_dir, ))
        assert(len(projects) == len(statuses))

        print('Converting to project instances...')
        for i, p in enumerate(projects):
            project = Project(p, statuses[i])
            self.data.append(project)

        # Convert to numpy arrays if needed
        # self.statuses = np.array(self.statuses)

        print("Data loaded.")

    def _load_project(self, project_id):
        """
        Load a saved project.

        :param project_id:  Id of project to load
        :return:
        """
        try:
            return self._load_binary("%s/project_%s.pkl" % (self.data_dir, project_id))
        except IOError:
            raise ProjectNotFound("Project %s not found" % project_id)


    def choose_n_projects(self, n=100):
        """
        Choose n projects randomly form the whole list of projects.

        :param n:   Number of projects to extract. If None or negative, take the whole list.
        :return:    Corresponding random indices, list of n projects
        """
        ind = np.random.random_integers(len(self.data), size=(n,))
        return self.data[ind]

    def histogram(self):
        # X, Y = project.difference_series(money)
        # hist, bins = np.histogram(Y, bins=50)
        # width = 0.7 * (bins[1] - bins[0])
        # center = (bins[:-1] + bins[1:]) / 2
        # plt.bar(center, hist, align='center', width=width)
        # plt.yscale('log')
        # plt.show()
        pass


class ProjectNotFound(DatasetError):
    def __init__(self, message):
        self.message = message