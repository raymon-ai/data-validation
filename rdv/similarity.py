class Serializable:

    @abc.abstractmethod
    def to_jdr(self):
        # Return a json-dumpable representation
        raise NotImplementedError()

    @abc.abstractmethod
    def load_jdr(self, jcr):
        # Load a json-dumpable representation
        raise NotImplementedError()


class MetricExtractor(Serializable):

    _config_attrs = []
    _compile_attrs = []

    def check_attrs(self, attributes):
        for attr in attributes:
            if not hasattr(self, attr) or getattr(self, attr) is None:
                return False
        return True

    def is_configured(self):
        return self.check_attrs(self._config_attrs)

    def is_compiled(self):
        return self.check_attrs(self._compile_attrs)

    def configure_interact(self, st, output):
        pass


class FixedSubpatchSimilarity(MetricExtractor):

    _config_attrs = ['patch']
    _compile_attrs = ['refs']

    def __init__(self, name, patch=None, refs=None):
        """[summary]

        Args:
            patch ([int], optional): [description]. The x0, y0, x1, y1 of the patch to look at.
            refs ([np.array], optional): [description]. References of what the patch should look like
        """
        self.name = name
        self.patch = patch
        self.refs = refs

    def to_jdr(self):
        pass

    def load_jdr(self, jcr):
        pass

    def configure(self, sl, data):
        st.sidebar.header(f"Configuring {self.name}")

        st.write("Active Image: ")
        active_img_idx = st.sidebar.number_input(label="Image index",
                                                 min_value=0,
                                                 max_value=len(loaded_images)-1, value=0, step=None, format="%d")
        active_img = loaded_images[active_img_idx].copy()
        img_size = active_img.size
        "Image dimensions: ", img_size
        # img = st.image(active_img)
        config_complete = st.sidebar.button("Commit Config")
        if not config_complete:
            x0 = st.sidebar.slider(label="Mask x0", min_value=0,
                                   max_value=img_size[0], value=0, step=1, format="%d", key=None)
            y0 = st.sidebar.slider(label="Mask y0", min_value=0,
                                   max_value=img_size[0], value=0, step=1, format="%d", key=None)
            sizex = st.sidebar.slider(label="Mask width", min_value=0,
                                      max_value=img_size[0], v alue=64, step=1, format="%d", key=None)
            sizey = st.sidebar.slider(label="Mask height", min_value=0,
                                      max_value=img_size[0], value=64, step=1, format="%d", key=None)

        else:
            st.
            st.sidebar.subheader("Add or remove sample from staging")
            add_button = st.sidebar.button(label="Add")
            rm_button = st.sidebar.button(label="Remove")
            if add_button:
                st.write("Save here")
            img = None

            if rm_button:
                st.write("Remove here")
