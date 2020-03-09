import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    user: JSON.parse(sessionStorage.getItem("addsCurrentUserInfo")) || {},
    token: ''
  },
  mutations: {
    saveUserInfo(state, userInfo) {
      state.user = userInfo;

      // Save "userInfo" to sessionStorage
      sessionStorage.setItem("addsCurrentUserInfo", JSON.stringify(userInfo));

      // Testing
      // console.log("Store -> saveUserInfo: ");
      // console.log(state.user);
    },
    clearUserInfo(state) {
      state.user = {};

      // Remove "userInfo" from sessionStorage
      sessionStorage.removeItem("addsCurrentUserInfo");

      // Testing
      // console.log("Store -> clearUserInfo: ");
      // console.log(state.user);
    }
  }
});

export default store;
